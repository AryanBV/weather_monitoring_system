# Weather Monitoring System

## Overview

This Weather Monitoring System is a Python-based application that fetches real-time weather data for multiple Indian metro cities, processes and stores this data, generates alerts for extreme weather conditions, and creates visualizations of weather trends.

## Core Features

- Fetches weather data from OpenWeatherMap API for Delhi, Mumbai, Chennai, Bangalore, Kolkata, and Hyderabad
- Processes and stores weather data in MongoDB
- Generates daily weather summaries including:
  - Average temperature
  - Maximum temperature
  - Minimum temperature
  - Dominant weather condition
- User-configurable alerts for temperature thresholds
- Visualizes daily weather summaries, historical trends, and triggered alerts

## Additional Features

- Extended weather parameters: Includes humidity and wind speed in addition to temperature
- 5-day weather forecast retrieval and processing
- Web dashboard for real-time weather visualization
- Machine learning-based weather prediction for the next 24 hours

    ### Web Dashboard
    The web dashboard provides a user-friendly interface to view current weather data, forecasts, and predictions for all monitored cities.

    ### Machine Learning Weather Prediction
    Trained machine learning models for 24-hour weather prediction are stored in the `models/` directory.

### Weather Monitoring System

To view the real-time weather dashboard:

- Ensure Flask is installed:
```pip install flask```
- Ensure you're in the project root directory.
- Run the Flask app:

```
python app.py
```

- Open a web browser and navigate to http://localhost:5000

The dashboard displays the latest weather data for all monitored cities in an easy-to-read format.

## Prerequisites

- Python 3.8+
- MongoDB
- OpenWeatherMap API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/AryanBV/weather_monitoring_system.git
   cd weather_monitoring_system
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up MongoDB:
   - Install MongoDB if you haven't already
   - Start the MongoDB service

4. Set up your OpenWeatherMap API key:
   - Sign up for a free API key at [OpenWeatherMap](https://openweathermap.org/api)
   - Set your API key as an environment variable:
     - On Windows:
       ```
       set OPENWEATHERMAP_API_KEY=your_api_key_here
       ```
     - On macOS/Linux:
       ```
       export OPENWEATHERMAP_API_KEY=your_api_key_here
       ```

5. Configure the application:
   - Open `config/config.yaml`
   - Adjust the MongoDB configuration if necessary
   - Modify alert thresholds and update intervals as desired

## Usage

To run the core Weather Monitoring System:

```
python main.py
```

To view the real-time weather dashboard (additional feature):

```
python app.py
```

Then open a web browser and navigate to `http://localhost:5000`

For a short demonstration run:

```
python run_demo.py
```

## Project Structure

```
weather_monitoring_system/
├── config/
│   └── config.yaml
├── logs/
├── models/
├── src/
│   ├── alerts/
│   │   ├── __init__.py
│   │   └── alert_manager.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── weather_api.py
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── aggregator.py
│   │   └── data_processor.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_handler.py
│   ├── ml/
│   │   └── weather_predictor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_loader.py
│   │   └── logger.py
│   └── visualization/
│       ├── __init__.py
│       └── visualizer.py
├── templates/
│   └── dashboard.html
├── tests/
│   ├── test_aggregator.py
│   ├── test_alert_manager.py
│   ├── test_data_processor.py
│   ├── test_db_handler.py
│   └── test_weather_api.py
├── visualizations/
├── app.py
├── main.py
├── README.md
├── requirements.txt
├── run_demo.py
└── test_system.py
```

## Configuration

You can modify the following in `config/config.yaml`:
- Database settings
- Alert thresholds (user-configurable)
- Data processing and visualization update intervals

The OpenWeatherMap API key should be set as an environment variable for security reasons.

## Logs

Logs are stored in the `logs/` directory. Check these for application activity and any errors.

## Visualizations

Weather trend visualizations are saved in the `visualizations/` directory.

## Testing

To run the system tests:

```
python test_system.py
```


Individual test files for different components can be found in the `tests/` directory.

## Test Cases

1. System Setup:
   - Verifies system starts successfully and connects to the OpenWeatherMap API using a valid API key.
2. Data Retrieval:
   - Simulates API calls at configurable intervals.
   - Ensures the system retrieves weather data for the specified locations and parses the response correctly.
3. Temperature Conversion:
   - Tests conversion of temperature values from Kelvin to Celsius.
4. Daily Weather Summary:
   - Simulates a sequence of weather updates for several days.
   - Verifies that daily summaries are calculated correctly, including average, maximum, minimum temperatures, and dominant weather condition.
5. Alerting Thresholds:
   - Defines and configures user thresholds for temperature conditions.
   - Simulates weather data exceeding or breaching the thresholds.
   - Verifies that alerts are triggered only when a threshold is violated.


## Troubleshooting

- If you encounter any issues with API key authentication, ensure that you've correctly set the `OPENWEATHERMAP_API_KEY` environment variable.
- For database connection issues, check your MongoDB service is running and the connection details in `config.yaml` are correct.
- If visualizations aren't generating, ensure you have write permissions in the `visualizations/` directory.

## Note

This project is an assignment submission. The implementation focuses on demonstrating understanding of real-time data processing, API integration, data aggregation, alerting systems, and visualization techniques in a weather monitoring context. Additional features showcase further capabilities beyond the core requirements.