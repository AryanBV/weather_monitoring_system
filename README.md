# Weather Monitoring System

## Overview

This Weather Monitoring System is a Python-based application that fetches real-time weather data for multiple cities, processes and stores this data, generates alerts for extreme weather conditions, and creates visualizations of weather trends.

## Features

- Fetches weather data from OpenWeatherMap API(temperature data is received in Celsius)
- Processes and stores weather data in MongoDB
- Generates daily weather summaries
- Alerts for high and low temperature thresholds
- Visualizes temperature trends and weather conditions
- Logs system activities and errors

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
   - Update the list of cities if needed
   - Adjust the MongoDB configuration if necessary
   - Modify alert thresholds and update intervals as desired

## Usage

To run the Weather Monitoring System:

```
python main.py
```

For a short demonstration run:

```
python run_demo.py
```

The application will start fetching weather data at regular intervals, process it, store it in the database, check for alerts, and generate visualizations.

## Project Structure

```
weather_monitoring_system/
├── src/
│   ├── api/
│   │   └── weather_api.py
│   ├── data_processing/
│   │   ├── data_processor.py
│   │   └── aggregator.py
│   ├── database/
│   │   └── db_handler.py
│   ├── alerts/
│   │   └── alert_manager.py
│   ├── visualization/
│   │   └── visualizer.py
│   └── utils/
│       ├── logger.py
│       └── config_loader.py
├── tests/
│   └── test_system.py
├── config/
│   └── config.yaml
├── logs/
│   └── ...
├── visualizations/
│   └── ...
├── requirements.txt
├── main.py
├── run_demo.py
└── README.md
```

## Configuration

You can modify the following in `config/config.yaml`:
- List of cities to monitor
- Database settings
- Alert thresholds (user-configurable)
- Data processing and visualization update intervals

The OpenWeatherMap API key should be set as an environment variable for security reasons.

## Logs

Logs are stored in the `logs/` directory. Check these for application activity and any errors.

## Visualizations

Weather trend visualizations are saved in the `visualizations/` directory.


## Test Cases

The `test_system.py` script covers the following test cases:

1. System Setup: Verifies successful connection to the OpenWeatherMap API.
2. Data Retrieval: Simulates API calls and checks correct data parsing.
3. Daily Weather Summary: Verifies correct calculation of daily summaries.
4. Alerting Thresholds: Tests alert triggering based on configured thresholds.

To run the tests:

```
python test_system.py
```

## Troubleshooting

- If you encounter any issues with API key authentication, ensure that you've correctly set the `OPENWEATHERMAP_API_KEY` environment variable.
- For database connection issues, check your MongoDB service is running and the connection details in `config.yaml` are correct.
- If visualizations aren't generating, ensure you have write permissions in the `visualizations/` directory.

## Note 

This project is an assignment submission. The implementation focuses on demonstrating understanding of system design, API integration, data processing, and visualization techniques. 