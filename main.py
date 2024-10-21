import os
import sys
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.api.weather_api import WeatherAPI
from src.data_processing.data_processor import DataProcessor
from src.database.db_handler import DBHandler
from src.alerts.alert_manager import AlertManager
from src.visualization.visualizer import Visualizer
from src.utils.logger import logger
from src.utils.config_loader import load_config

def main():
    config = load_config()
    
    weather_api = WeatherAPI(config['api_key'])
    data_processor = DataProcessor()
    db_handler = DBHandler(config['database'])
    alert_manager = AlertManager(config['alert_thresholds'])
    visualizer = Visualizer()

    update_interval = config['data_processing']['update_interval']

    while True:
        try:
            logger.info("Starting data update cycle")
            
            # Fetch current weather data
            raw_data = weather_api.get_weather_data(config['cities'])
            processed_data = data_processor.process(raw_data)
            db_handler.store_weather_data(processed_data)
            
            daily_summary = data_processor.calculate_daily_summary(processed_data)
            db_handler.store_daily_summary(daily_summary)
            
            # Fetch and process forecast data
            forecast_data = weather_api.get_forecast_data(config['cities'])
            processed_forecast = data_processor.process_forecast(forecast_data)
            forecast_summary = data_processor.summarize_forecast(processed_forecast)
            db_handler.store_forecast_summary(forecast_summary)
            
            alerts = alert_manager.check_thresholds(processed_data)
            if alerts:
                alert_manager.send_alerts(alerts)
            
            visualizer.update_visualizations(daily_summary, forecast_summary, alerts)

            logger.info(f"Data update completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            time.sleep(update_interval)

        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()