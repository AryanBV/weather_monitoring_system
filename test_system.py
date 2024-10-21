import yaml
from src.api.weather_api import WeatherAPI
from src.data_processing.data_processor import DataProcessor
from src.database.db_handler import DBHandler
from src.alerts.alert_manager import AlertManager
from src.visualization.visualizer import Visualizer
from src.utils.logger import logger
from datetime import datetime, timedelta

def load_config():
    with open('config/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def test_system():
    config = load_config()
    
    # Test 1: System Setup
    logger.info("Test 1: System Setup")
    weather_api = WeatherAPI(config['api_key'])
    assert weather_api is not None, "Failed to initialize WeatherAPI"
    
    # Test 2: Current Weather Data Retrieval
    logger.info("Test 2: Current Weather Data Retrieval")
    raw_data = weather_api.get_weather_data(config['cities'])
    assert len(raw_data) == len(config['cities']), "Data not retrieved for all cities"
    
    # Test 3: Forecast Data Retrieval
    logger.info("Test 3: Forecast Data Retrieval")
    forecast_data = weather_api.get_forecast_data(config['cities'])
    assert len(forecast_data) == len(config['cities']), "Forecast data not retrieved for all cities"
    
    # Test 4: Data Processing
    logger.info("Test 4: Data Processing")
    data_processor = DataProcessor()
    processed_data = data_processor.process(raw_data)
    processed_forecast = data_processor.process_forecast(forecast_data)
    
    assert len(processed_data) == len(raw_data), "Not all current weather data processed"
    assert len(processed_forecast) == len(forecast_data), "Not all forecast data processed"
    
    # Test 5: Daily Weather Summary
    logger.info("Test 5: Daily Weather Summary")
    daily_summary = data_processor.calculate_daily_summary(processed_data)
    assert len(daily_summary) > 0, "Daily summary not calculated"
    
    # Verify summary calculations
    for summary in daily_summary:
        assert 'avg_temperature' in summary, "Average temperature not calculated"
        assert 'max_temperature' in summary, "Maximum temperature not calculated"
        assert 'min_temperature' in summary, "Minimum temperature not calculated"
        assert 'avg_humidity' in summary, "Average humidity not calculated"
        assert 'avg_wind_speed' in summary, "Average wind speed not calculated"
        assert 'dominant_condition' in summary, "Dominant condition not determined"
    
    # Test 6: Forecast Summary
    logger.info("Test 6: Forecast Summary")
    forecast_summary = data_processor.summarize_forecast(processed_forecast)
    assert len(forecast_summary) == len(config['cities']), "Forecast summary not calculated for all cities"
    
    # Test 7: Database Operations
    logger.info("Test 7: Database Operations")
    db_handler = DBHandler(config['database'])
    db_handler.store_weather_data(processed_data)
    db_handler.store_daily_summary(daily_summary)
    db_handler.store_forecast_summary(forecast_summary)
    
    # Test data retrieval
    test_city = config['cities'][0]
    recent_data = db_handler.get_recent_weather_data(test_city, limit=1)
    assert len(recent_data) == 1, "Recent data not retrieved from database"
    
    # Test 8: Alerting Thresholds
    logger.info("Test 8: Alerting Thresholds")
    alert_manager = AlertManager(config['alert_thresholds'])
    alerts = alert_manager.check_thresholds(processed_data)
    
    # Simulate threshold breach
    high_temp = config['alert_thresholds']['high_temperature'] + 1
    consecutive_updates = config['alert_thresholds']['consecutive_updates']
    simulated_data = [
        {
            'city': test_city,
            'temperature': high_temp,
            'timestamp': datetime.now() + timedelta(minutes=i*5)
        } for i in range(consecutive_updates)
    ]
    
    for data in simulated_data:
        new_alerts = alert_manager.check_thresholds([data])
        alerts.extend(new_alerts)
    
    assert len(alerts) > 0, f"Alert not triggered for threshold breach in {test_city}"
    
    # Test 9: Visualization
    logger.info("Test 9: Visualization")
    visualizer = Visualizer()
    visualizer.update_visualizations(daily_summary, forecast_summary, alerts)
    
    logger.info("All tests completed successfully!")

if __name__ == "__main__":
    test_system()