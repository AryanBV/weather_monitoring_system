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
    
    # Test 2: Data Retrieval
    logger.info("Test 2: Data Retrieval")
    raw_data = weather_api.get_weather_data(config['cities'])
    assert len(raw_data) == len(config['cities']), "Data not retrieved for all cities"
    
    # Test 3: Temperature Conversion (not needed as we receive data in Celsius)
    logger.info("Test 3: Temperature Conversion (Skipped - data already in Celsius)")
    
    # Test 4: Daily Weather Summary
    logger.info("Test 4: Daily Weather Summary")
    data_processor = DataProcessor()
    processed_data = data_processor.process(raw_data)
    daily_summary = data_processor.calculate_daily_summary(processed_data)
    assert len(daily_summary) > 0, "Daily summary not calculated"
    
    # Verify summary calculations
    for summary in daily_summary:
        assert 'avg_temperature' in summary, "Average temperature not calculated"
        assert 'max_temperature' in summary, "Maximum temperature not calculated"
        assert 'min_temperature' in summary, "Minimum temperature not calculated"
        assert 'dominant_condition' in summary, "Dominant condition not determined"
    
    # Test 5: Alerting Thresholds
    logger.info("Test 5: Alerting Thresholds")
    alert_manager = AlertManager(config['alert_thresholds'])
    alerts = alert_manager.check_thresholds(processed_data)
    
    # Simulate threshold breach for a real city (e.g., Delhi)
    test_city = config['cities'][0]  # Using the first city in the config
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
    assert alerts[-1]['type'] == 'high_temperature', f"Incorrect alert type for {test_city}"
    assert alerts[-1]['temperature'] == high_temp, f"Incorrect alert temperature for {test_city}"
    assert alerts[-1]['city'] == test_city, f"Alert triggered for wrong city. Expected {test_city}"
    
    # Test visualization
    logger.info("Testing Visualizer")
    visualizer = Visualizer()
    visualizer.update_visualizations(daily_summary, alerts)
    
    logger.info("All tests completed successfully!")

if __name__ == "__main__":
    test_system()