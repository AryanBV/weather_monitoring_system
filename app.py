from flask import Flask, render_template
from src.data_processing.data_processor import DataProcessor
from src.database.db_handler import DBHandler
from src.utils.config_loader import load_config
import os

app = Flask(__name__)

config = load_config()
db_handler = DBHandler(config['database'])
data_processor = DataProcessor()

@app.route('/')
def dashboard():
    cities = db_handler.get_cities()
    latest_data = {}
    for city in cities:
        city_data = db_handler.get_recent_weather_data(city, limit=1)
        if city_data:
            latest_data[city] = city_data[0]
    
    return render_template('dashboard.html', latest_data=latest_data)

if __name__ == '__main__':
    app.run(debug=True)