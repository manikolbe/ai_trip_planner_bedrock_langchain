import streamlit as st
import requests
from langchain_aws import ChatBedrock
from langchain.schema import SystemMessage, HumanMessage
import re

# Initialize LLM with LangChain
llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    credentials_profile_name="default",
    region_name="us-east-1",
)

# Function to get coordinates from city name using Nominatim
def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    headers = {
        "User-Agent": "TripItineraryPlanner/1.0 (test@example.com)"  # Replace with your app name and contact info
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        location_data = response.json()
        if location_data:
            location = location_data[0]
            return float(location['lat']), float(location['lon'])
        else:
            st.warning("City not found. Please check the spelling or try adding the country name (e.g., 'Paris, France').")
            return None, None
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None, None

# Function to get weather data from Open-Meteo
def get_weather_data(lat, lon, start_date, end_date):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        daily_data = data.get("daily", {})
        # Format weather data as a text summary
        weather_summary = []
        for i in range(len(daily_data["time"])):
            weather_summary.append(
                f"- **Date:** {daily_data['time'][i]}, **Max Temp:** {daily_data['temperature_2m_max'][i]}°C, "
                f"**Min Temp:** {daily_data['temperature_2m_min'][i]}°C, **Precipitation:** {daily_data['precipitation_sum'][i]} mm."
            )
        return "\n".join(weather_summary)
    else:
        return "Weather data not available."

# Function to generate the prompt for the itinerary
def generate_prompt(input_data, weather_summary, attractions_data):
    """
    Generates a prompt string for the itinerary based on input data, weather summary, and attractions data.

    Args:
        input_data (dict): Contains trip details and traveler information.
        weather_summary (str): Summary of the weather forecast for the trip.
        attractions_data (str): Information about available attractions and activities.

    Returns:
        str: The formatted prompt to be sent to the LLM.
    """
    travelers = "\n".join(
        [
            f"- **{t['name']}** (Age: {t['age']}): {t['preferences']}"
            for t in input_data.get("travelers", [])
        ]
    )
    
    prompt = f"""
    Generate a detailed itinerary for the following trip using markdown formatting:

    **Origin:** {input_data.get('origin', 'N/A')}  
    **Destination:** {input_data.get('destination', 'N/A')}  
    **Start Date:** {input_data.get('start_date', 'N/A')}  
    **Arrival Time:** {input_data.get('arrival_time', 'N/A')}  
    **End Date:** {input_data.get('end_date', 'N/A')}  
    **Departure Time:** {input_data.get('departure_time', 'N/A')}  

    **Travelers:**
    {travelers if travelers else 'N/A'}

    **Weather Forecast for the Trip:**
    {weather_summary if weather_summary else 'N/A'}

    **Available Attractions and Activities:**
    {attractions_data if attractions_data else 'N/A'}

    **Instructions:**
    - Organize the itinerary day-by-day.
    - Use headers for each day (e.g., ## Day 1: [Date] [Day of the week]).
    - For each day, list activities under **Morning**, **Afternoon**, and **Evening** as bold text (e.g., **Morning**).
    - Use bullet points for activities.
    - Ensure the formatting is clean and easy to read.
    - Consider weather conditions and traveler preferences.
    """
    print(f"--Generated prompt--\n{prompt.strip()}")
    return prompt.strip()

# Function to generate the itinerary using LangChain LLM
def generate_itinerary(input_data, weather_summary, attractions_data):
    """
    Generates a detailed itinerary by interacting with the LangChain LLM.

    Args:
        input_data (dict): Contains trip details and traveler information.
        weather_summary (str): Summary of the weather forecast for the trip.
        attractions_data (str): Information about available attractions and activities.
        llm: An instance of the LangChain LLM (e.g., ChatBedrock).

    Returns:
        str: The generated itinerary content from the LLM.
    """
    # Define the system message to set the context for the LLM
    system_message_content = (
        "You are a professional travel advisor. Your role is to create detailed and personalized travel itineraries for clients. "
        "When planning itineraries, you must consider travelers' preferences, including their interests and preferred activities. "
        "Take into account the travelers' origin locations—for instance, individuals from colder climates may prefer beach destinations in warmer countries. "
        "Additionally, consider the ages of the travelers, whether they are traveling as a family, and other relevant demographics. "
        "For families, do not stack up too many things. Allow breaks in between. Also, families always do things together"
        "Always factor in the weather conditions during the trip dates to ensure the itinerary is practical and enjoyable."
    )
    system_message = SystemMessage(content=system_message_content)
    
    # Generate the prompt based on input data
    prompt = generate_prompt(input_data, weather_summary, attractions_data)
    human_message = HumanMessage(content=prompt)
    
    # Create a list of messages including the system message and the human message
    messages = [system_message, human_message]
    
    # Get the response from the LLM
    response = llm(messages)
    
    return response.content

# Function to parse itinerary into days
def parse_itinerary(markdown_text):
    """
    Parses the markdown itinerary and returns a list of days with their content.
    """
    days = re.split(r'## Day \d+: \d{4}-\d{2}-\d{2}', markdown_text)
    headers = re.findall(r'## Day \d+: \d{4}-\d{2}-\d{2}', markdown_text)
    itinerary_days = []
    for header, content in zip(headers, days[1:]):
        day_title = header.strip('# ').strip()
        itinerary_days.append((day_title, content.strip()))
    return itinerary_days

# Streamlit UI
st.title("Trip Itinerary Planner")

# Initialize session state
if "input_data" not in st.session_state:
    st.session_state["input_data"] = {}
if "travelers" not in st.session_state:
    st.session_state["travelers"] = []

if st.session_state["input_data"]:
    # Show details in the sidebar
    with st.sidebar:
        st.title("Trip Details")
        st.write("**Start:**", st.session_state["input_data"]["start_date"], st.session_state["input_data"]["arrival_time"])
        st.write("**End:**", st.session_state["input_data"]["end_date"], st.session_state["input_data"]["departure_time"])

        st.write("**Travelers:**")
        for idx, traveler in enumerate(st.session_state["travelers"], start=1):
            st.write(f"{traveler['name']} (Age: {traveler['age']})")
            st.write(f" - Preferences: {traveler['preferences']}")
            st.write("")
    
    destination = st.session_state["input_data"]["destination"]
    start_date = st.session_state["input_data"]["start_date"]
    end_date = st.session_state["input_data"]["end_date"]

    # Fetch Coordinates and Weather Data
    lat, lon = get_coordinates(destination)
    if lat and lon:
        weather_summary = get_weather_data(lat, lon, start_date, end_date)
        attractions_data = "Sample attractions data placeholder."  # Replace with actual attractions API
        itinerary = generate_itinerary(st.session_state["input_data"], weather_summary, attractions_data)
        
        st.write("### Generated Itinerary")
        # Option 1: Direct Markdown Rendering
        # st.markdown(itinerary, unsafe_allow_html=True)
        
        # Option 2: Using Expanders for Each Day
        # Uncomment the following lines if you prefer using expanders
        itinerary_days = parse_itinerary(itinerary)
        for day, content in itinerary_days:
            with st.expander(day, expanded=True):
                st.markdown(content)
        
    else:
        st.error("Could not fetch location data. Please check the destination.")
else:
    # Collect trip details
    st.write("### Trip Details")
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("Origin", value="London")
    with col2:
        destination = st.text_input("Destination", value="Dubai")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        trip_arrival_date = st.date_input("Arrival Date")
    with col2:
        arrival_time = st.time_input("Arrival Time")
    with col3:
        trip_end_date = st.date_input("End Date")
    with col4:
        departure_time = st.time_input("Departure Time")

    num_travelers = st.number_input("Number of Travelers", min_value=1, step=1, key="num_travelers")

    st.write("### Add Traveler Details")
    for i in range(num_travelers):
        with st.expander(f"Traveler {i+1}", expanded=False):
            st.text_input("Name", key=f"name_{i+1}")
            st.number_input("Age", min_value=0, key=f"age_{i+1}")
            st.text_area("Preferences", key=f"preferences_{i+1}")

    if st.button("Plan My Trip"):
        new_travelers = []
        for i in range(num_travelers):
            t_name = st.session_state.get(f"name_{i+1}", "").strip()
            t_age = st.session_state.get(f"age_{i+1}", None)
            t_pref = st.session_state.get(f"preferences_{i+1}", "").strip()

            if not t_name or t_age is None:
                st.error(f"Please fill in all details for Traveler {i+1} before finalizing.")
                st.stop()
            else:
                new_travelers.append({
                    "name": t_name,
                    "age": t_age,
                    "preferences": t_pref,
                })

        st.session_state["travelers"] = new_travelers
        st.session_state["input_data"] = {
            "origin": origin.strip(),
            "destination": destination.strip(),
            "start_date": trip_arrival_date,
            "end_date": trip_end_date,
            "arrival_time": arrival_time,
            "departure_time": departure_time,
            "travelers": new_travelers,
        }
        st.rerun()