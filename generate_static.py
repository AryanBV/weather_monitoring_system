import os
import json
import shutil
from datetime import datetime, timedelta
from flask import render_template
from jinja2 import Environment, FileSystemLoader
from src.database.db_handler import DBHandler
from src.utils.config_loader import load_config
from src.utils.logger import logger
from src.api.weather_api import WeatherAPI

# Load configuration
config = load_config()
db_handler = DBHandler(config['database'])

# Create build directory if it doesn't exist
build_dir = 'build'
if not os.path.exists(build_dir):
    os.makedirs(build_dir)

# Copy static assets if they exist
assets_dir = 'static'
if os.path.exists(assets_dir):
    if not os.path.exists(os.path.join(build_dir, 'static')):
        os.makedirs(os.path.join(build_dir, 'static'))
    for file in os.listdir(assets_dir):
        shutil.copy2(os.path.join(assets_dir, file), os.path.join(build_dir, 'static', file))

# Copy visualizations
viz_dir = 'visualizations'
if os.path.exists(viz_dir):
    if not os.path.exists(os.path.join(build_dir, 'visualizations')):
        os.makedirs(os.path.join(build_dir, 'visualizations'))
    for file in os.listdir(viz_dir):
        if file.endswith('.png'):
            shutil.copy2(os.path.join(viz_dir, file), os.path.join(build_dir, 'visualizations', file))

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

# Get data for dashboard
cities = db_handler.get_cities()
latest_data = {}
predictions = {}
prediction_errors = {}

# Function to prepare city data
def prepare_city_data(city_data):
    if not city_data:
        return {
            'city': 'Unknown',
            'temperature': 'N/A',
            'feels_like': 'N/A',
            'humidity': 'N/A',
            'wind_speed': 'N/A',
            'weather_condition': 'No Data',
            'timestamp': datetime.now()
        }
    
    city_record = city_data.copy()
    if not isinstance(city_record.get('timestamp'), datetime):
        city_record['timestamp'] = (
            city_record.get('timestamp') if isinstance(city_record.get('timestamp'), datetime)
            else datetime.fromtimestamp(city_record.get('dt', datetime.now().timestamp()))
        )
    
    default_keys = {
        'city': 'Unknown',
        'temperature': 'N/A',
        'feels_like': 'N/A',
        'humidity': 'N/A',
        'wind_speed': 'N/A',
        'weather_condition': 'No Data'
    }
    
    for key, default_value in default_keys.items():
        city_record[key] = city_record.get(key, default_value)
    
    return city_record

# Fetch AQI data
aqi_data = {}
try:
    if cities:
        weather_api = WeatherAPI(config['api_key'])
        aqi_data = weather_api.get_air_quality_data(cities)
except Exception as e:
    logger.error(f"Error fetching AQI data: {str(e)}")

# Get data for each city
for city in cities:
    try:
        city_data_list = db_handler.get_recent_weather_data(city, limit=1)
        city_data = prepare_city_data(city_data_list[0] if city_data_list else None)
        latest_data[city] = city_data
        
        # Static prediction as we can't use ML models easily in static generation
        # You could generate and save predictions separately
        predictions[city] = "See dashboard for live predictions"
    except Exception as e:
        logger.error(f"Error processing data for {city}: {str(e)}")
        latest_data[city] = prepare_city_data(None)
        predictions[city] = "N/A"

# Generate dashboard.html
try:
    template = env.get_template('dashboard.html')
    output = template.render(
        latest_data=latest_data,
        predictions=predictions,
        prediction_errors=prediction_errors,
        aqi_data=aqi_data,
        datetime=datetime
    )
    
    with open(os.path.join(build_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(output)
    
    logger.info("Successfully generated dashboard.html")
except Exception as e:
    logger.error(f"Error generating dashboard.html: {str(e)}")

# Generate historical data pages for each city
for city in cities:
    try:
        # Generate for 7 days by default
        days = 7
        start_date = datetime.now() - timedelta(days=days)
        historical_data = db_handler.get_historical_weather_data(city, days=days)
        
        dates = []
        temps = []
        humidity = []
        wind = []
        
        for record in historical_data:
            if 'timestamp' in record:
                dates.append(record['timestamp'].strftime('%Y-%m-%d %H:%M'))
                temps.append(record.get('temperature', 0))
                humidity.append(record.get('humidity', 0))
                wind.append(record.get('wind_speed', 0))
        
        # Create city directory
        city_dir = os.path.join(build_dir, 'historical', city)
        os.makedirs(city_dir, exist_ok=True)
        
        # Render template
        template = env.get_template('historical.html')
        output = template.render(
            city=city,
            dates=json.dumps(dates),
            temps=json.dumps(temps),
            humidity=json.dumps(humidity),
            wind=json.dumps(wind),
            days=days,
            data_count=len(historical_data)
        )
        
        with open(os.path.join(city_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(output)
        
        logger.info(f"Successfully generated historical data page for {city}")
    except Exception as e:
        logger.error(f"Error generating historical data page for {city}: {str(e)}")

# Close DB connection
db_handler.close()
logger.info("Static site generation completed")