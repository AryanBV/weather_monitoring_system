from flask import Flask, render_template
from src.data_processing.data_processor import DataProcessor
from src.database.db_handler import DBHandler
from src.utils.config_loader import load_config
from src.ml.weather_predictor import WeatherPredictor
from datetime import datetime, timedelta
import os

app = Flask(__name__)

config = load_config()
db_handler = DBHandler(config['database'])
data_processor = DataProcessor()

@app.route('/')
def dashboard():
    cities = db_handler.get_cities()
    latest_data = {}
    predictions = {}
    for city in cities:
        city_data = db_handler.get_recent_weather_data(city, limit=1)
        if city_data:
            latest_data[city] = city_data[0]
            predictor = WeatherPredictor(city)
            try:
                predictor.load_model()
            except FileNotFoundError:
                historical_data = db_handler.get_historical_weather_data(city)
                if historical_data:
                    predictor.train_model(historical_data)
                else:
                    continue  # Skip prediction if no historical data

            next_day = datetime.now() + timedelta(days=1)
            try:
                prediction = predictor.predict(
                    next_day.hour,
                    next_day.weekday(),
                    next_day.month,
                    latest_data[city]['humidity'],
                    latest_data[city]['wind_speed'],
                    latest_data[city]['weather_condition']
                )
                predictions[city] = round(prediction, 1)
            except ValueError as e:
                print(f"Prediction error for {city}: {str(e)}")
                predictions[city] = "N/A"
    
    return render_template('dashboard.html', latest_data=latest_data, predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)