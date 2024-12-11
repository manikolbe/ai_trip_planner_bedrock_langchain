# Trip Itinerary Planner

## Overview

The **Trip Itinerary Planner** is a web-based application built using Streamlit that allows users to create personalized travel itineraries. It integrates various APIs and AI models to generate detailed day-by-day travel plans based on user input, weather forecasts, and attractions.

## Features

- **User-friendly Interface**: Input trip details, traveler preferences, and receive a tailored itinerary.
- **AI-Powered Itinerary Generation**: Utilizes AWS Bedrock's Claude model via LangChain to generate professional travel plans.
- **Weather Forecast Integration**: Retrieves weather data using the Open-Meteo API to customize itineraries.
- **Dynamic City Lookup**: Fetches location coordinates using Nominatim's OpenStreetMap API.
- **Expandable Itinerary View**: View daily plans with clean markdown formatting.

## Requirements

- Python 3.8+
- Streamlit
- Requests library
- LangChain AWS integration

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/manikolbe/ai_trip_planner_bedrock_langchain.git
   cd trip-itinerary-planner
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up AWS credentials for the LangChain Bedrock integration. Ensure you have the appropriate permissions to access the Bedrock service.

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open the app in your web browser (default: `http://localhost:8501`).

3. Follow these steps:
   - Enter the trip details: origin, destination, travel dates, and number of travelers.
   - Add traveler-specific preferences and demographics.
   - Click on "Plan My Trip" to generate the itinerary.

## API Integrations

### 1. Nominatim (OpenStreetMap)

- Purpose: Fetch city coordinates.
- Endpoint: `https://nominatim.openstreetmap.org/search`

### 2. Open-Meteo

- Purpose: Retrieve weather forecasts.
- Endpoint: `https://api.open-meteo.com/v1/forecast`

### 3. AWS Bedrock (via LangChain)

- Purpose: Use Claude AI to generate detailed travel itineraries.

## Customization

### Adjusting the Itinerary Prompt

The system prompt and user prompt for the AI model can be customized in the `generate_prompt` and `generate_itinerary` functions to adapt the itinerary style or include additional details.

### Adding Attractions Data

Replace the placeholder `attractions_data` with data fetched from a reliable API to provide more tailored activity recommendations.

## Example Output

### Sample Input

- **Origin**: London
- **Destination**: Dubai
- **Start Date**: 2024-12-23
- **End Date**: 2024-12-28
- **Travelers**:
  - John (Age: 42, Preferences: Beaches, Adventure sports)
  - Sarah (Age: 40, Preferences: Cultural tours, Shopping)

### Sample Itinerary

#### **Day 1: 2024-12-23 (Monday)**

- **Morning**:
  - Arrival at Dubai International Airport.
  - Check-in at the hotel.
- **Afternoon**:
  - Visit Dubai Mall for lunch and shopping.
- **Evening**:
  - Explore the Dubai Fountain show.

... (more days follow)

## Known Limitations

- The app currently uses placeholder attractions data.
- Dependent on accurate input; incorrect city names may result in failed API calls.
- Requires internet connectivity for API access.
