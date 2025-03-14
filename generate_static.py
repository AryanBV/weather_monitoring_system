import os
import json
import shutil
from datetime import datetime, timedelta
import traceback
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Create required directories
def ensure_directories():
    directories = ['build', 'static', 'visualizations', 'models']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
    # Create subdirectory for historical pages
    Path('build/historical').mkdir(exist_ok=True)

# Main function with error handling
def generate_static_files():
    print("Starting static file generation...")
    
    try:
        from src.utils.config_loader import load_config
        from src.utils.logger import logger
        
        # Make sure required directories exist
        ensure_directories()
        print("Created required directories")
        
        # Load configuration
        try:
            config = load_config()
            print("Successfully loaded configuration")
        except Exception as e:
            print(f"Warning: Error loading configuration: {e}")
            # Create minimal config if loading fails
            config = {
                'api_key': os.environ.get('OPENWEATHERMAP_API_KEY', ''),
                'cities': ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad'],
                'database': {
                    'host': 'localhost',
                    'port': 27017,
                    'name': 'weather_monitoring'
                }
            }
        
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Copy static assets if they exist
        static_dir = 'static'
        if os.path.exists(static_dir):
            if not os.path.exists(os.path.join('build', 'static')):
                os.makedirs(os.path.join('build', 'static'))
            for file in os.listdir(static_dir):
                src_path = os.path.join(static_dir, file)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, os.path.join('build', 'static', file))
        
        # Copy visualizations
        viz_dir = 'visualizations'
        if os.path.exists(viz_dir):
            if not os.path.exists(os.path.join('build', 'visualizations')):
                os.makedirs(os.path.join('build', 'visualizations'))
            for file in os.listdir(viz_dir):
                if file.endswith('.png'):
                    src_path = os.path.join(viz_dir, file)
                    if os.path.isfile(src_path):
                        shutil.copy2(src_path, os.path.join('build', 'visualizations', file))
        
        # Try to connect to database and get data
        try:
            from src.database.db_handler import DBHandler
            db_handler = DBHandler(config['database'])
            cities = db_handler.get_cities()
            print(f"Successfully connected to database and found {len(cities)} cities")
        except Exception as e:
            print(f"Warning: Error connecting to database: {e}")
            # Use cities from config if DB connection fails
            cities = config['cities']
            print(f"Using cities from config: {', '.join(cities)}")
            db_handler = None
        
        # Generate a simple index.html if we can't properly connect to the database
        if not db_handler or not cities:
            print("Generating fallback index.html...")
            
            # Create a simple HTML content
            html_content = """<!DOCTYPE html>
            <html>
            <head>
                <title>Weather Monitoring System</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
                    h1 { color: #0066cc; }
                </style>
            </head>
            <body>
                <h1>Weather Monitoring System</h1>
                <p>Welcome to the Weather Monitoring System Dashboard. This is a static placeholder page.</p>
                <p>This dashboard will show live weather data once the data collection process completes.</p>
                <p>Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </body>
            </html>"""
            
            with open(os.path.join('build', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("Generated fallback index.html")
            return
        
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
        
        # Get data for dashboard
        latest_data = {}
        predictions = {}
        prediction_errors = {}
        aqi_data = {}
        
        for city in cities:
            try:
                # Get recent data
                city_data_list = db_handler.get_recent_weather_data(city, limit=1)
                city_data = prepare_city_data(city_data_list[0] if city_data_list else None)
                latest_data[city] = city_data
                
                # Use placeholder predictions
                predictions[city] = "See dashboard for live predictions"
            except Exception as e:
                print(f"Warning: Error processing data for {city}: {e}")
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
            
            with open(os.path.join('build', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(output)
            
            print("Successfully generated dashboard.html as index.html")
        except Exception as e:
            print(f"Error generating dashboard.html: {str(e)}")
            print(traceback.format_exc())
        
        # Generate historical data pages for each city
        for city in cities:
            try:
                # Create city directory
                city_dir = os.path.join('build', 'historical', city)
                os.makedirs(city_dir, exist_ok=True)
                
                # Get minimal historical data
                historical_data = db_handler.get_historical_weather_data(city, days=7) if db_handler else []
                
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
                
                # Render template
                template = env.get_template('historical.html')
                output = template.render(
                    city=city,
                    dates=json.dumps(dates),
                    temps=json.dumps(temps),
                    humidity=json.dumps(humidity),
                    wind=json.dumps(wind),
                    days=7,
                    data_count=len(historical_data)
                )
                
                with open(os.path.join(city_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(output)
                
                print(f"Successfully generated historical data page for {city}")
            except Exception as e:
                print(f"Error generating historical data page for {city}: {str(e)}")
        
        # Close DB connection
        if db_handler:
            db_handler.close()
        
        print("Static site generation completed successfully")
        
    except Exception as e:
        print(f"Critical error in static file generation: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    generate_static_files()