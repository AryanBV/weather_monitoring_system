from dotenv import load_dotenv
from flask import Flask, render_template
from src.data_processing.data_processor import DataProcessor
from src.database.db_handler import DBHandler
from src.utils.config_loader import load_config
from src.ml.weather_predictor import WeatherPredictor
from src.utils.logger import logger  # Add logger import
from datetime import datetime, timedelta
import os
import traceback

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

config = load_config()
db_handler = DBHandler(config['database'])
data_processor = DataProcessor()

def prepare_city_data(city_data):
    """Prepare city data with consistent timestamp and default values"""
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
    
    # Ensure timestamp is a datetime object
    city_record = city_data.copy()
    if not isinstance(city_record.get('timestamp'), datetime):
        city_record['timestamp'] = (
            city_record.get('timestamp') if isinstance(city_record.get('timestamp'), datetime)
            else datetime.fromtimestamp(city_record.get('dt', datetime.now().timestamp()))
        )
    
    # Add default values for any missing keys
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

@app.route('/')
def dashboard():
    try:
        cities = db_handler.get_cities()
        latest_data = {}
        predictions = {}
        prediction_errors = {}
        
        for city in cities:
            try:
                city_data_list = db_handler.get_recent_weather_data(city, limit=1)
                city_data = prepare_city_data(city_data_list[0] if city_data_list else None)
                latest_data[city] = city_data
                
                predictor = WeatherPredictor(city)
                
                try:
                    predictor.load_model()
                except FileNotFoundError:
                    logger.info(f"No model found for {city}, attempting to train one")
                    historical_data = db_handler.get_historical_weather_data(city)
                    if historical_data and len(historical_data) > 10:  # Need sufficient data to train
                        predictor.train_model(historical_data)
                    else:
                        prediction_errors[city] = "Insufficient historical data for training"
                        continue

                next_day = datetime.now() + timedelta(days=1)
                try:
                    prediction = predictor.predict(
                        next_day.hour,
                        next_day.weekday(),
                        next_day.month,
                        city_data.get('humidity', 50),
                        city_data.get('wind_speed', 0),
                        city_data.get('weather_condition', 'Clear')
                    )
                    predictions[city] = round(prediction, 1)
                except ValueError as e:
                    error_msg = f"Prediction error for {city}: {str(e)}"
                    logger.error(error_msg)
                    prediction_errors[city] = error_msg
                    predictions[city] = "N/A"
            except Exception as e:
                logger.error(f"Error processing data for {city}: {str(e)}")
                prediction_errors[city] = f"Error: {str(e)}"
                latest_data[city] = prepare_city_data(None)
        
        return render_template('dashboard.html', 
                              latest_data=latest_data, 
                              predictions=predictions, 
                              prediction_errors=prediction_errors,
                              datetime=datetime)  # Pass datetime to the template
    except Exception as e:
        logger.error(f"Dashboard rendering error: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)