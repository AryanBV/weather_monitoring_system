from src.database.db_handler import DBHandler
from src.utils.config_loader import load_config
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def main():
    print("Checking database for historical weather data...")
    
    # Load configuration
    try:
        config = load_config()
        print(f"Successfully loaded configuration")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Initialize database connection
    try:
        db_handler = DBHandler(config['database'])
        print(f"Successfully connected to MongoDB at {config['database']['host']}:{config['database']['port']}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Get list of cities
    try:
        cities = db_handler.get_cities()
        print(f"Found {len(cities)} cities in the database: {', '.join(cities)}")
    except Exception as e:
        print(f"Error getting cities: {e}")
        cities = config['cities']
        print(f"Using cities from config: {', '.join(cities)}")
    
    # Check for data for each city
    for city in cities:
        print(f"\nChecking data for: {city}")
        
        # Get recent data
        recent = db_handler.get_recent_weather_data(city, limit=1)
        if recent:
            print(f"✓ Recent data available: {recent[0]['timestamp']} ({recent[0].get('temperature')}°C)")
        else:
            print(f"✗ No recent data found")
        
        # Get historical data
        historical = db_handler.get_historical_weather_data(city, days=7)
        if historical:
            print(f"✓ Historical data available: {len(historical)} records")
            earliest = min([h['timestamp'] for h in historical])
            latest = max([h['timestamp'] for h in historical])
            print(f"  - Date range: {earliest} to {latest}")
        else:
            print(f"✗ No historical data found")
    
    # Check if this is a data collection issue or a data retrieval issue
    print("\nDiagnosing potential issues:")
    
    # Check DB collections directly
    try:
        weather_count = db_handler.weather_collection.count_documents({})
        summary_count = db_handler.summary_collection.count_documents({})
        forecast_count = db_handler.forecast_collection.count_documents({})
        
        print(f"Total documents in collections:")
        print(f"- weather_data: {weather_count} documents")
        print(f"- daily_summaries: {summary_count} documents")
        print(f"- forecast_data: {forecast_count} documents")
        
        if weather_count == 0:
            print("⚠️ No weather data in database - the data collection process is not working correctly")
        
    except Exception as e:
        print(f"Error accessing collections directly: {e}")
    
    # Close connection
    db_handler.close()
    
    # Provide recommendations
    print("\nPossible solutions:")
    print("1. Run the data collection script: python main.py")
    print("2. Run the demo for 10 minutes to collect more data: python run_demo.py")
    print("3. Create sample data (see generate_sample_data function below)")

def generate_sample_data():
    """Generate sample historical data for testing purposes"""
    config = load_config()
    db_handler = DBHandler(config['database'])
    
    cities = config['cities']
    print(f"Generating sample data for {len(cities)} cities...")
    
    # Create 7 days of historical data
    sample_data = []
    now = datetime.now()
    
    for city in cities:
        base_temp = {"Delhi": 28, "Mumbai": 30, "Chennai": 32, "Bangalore": 26, "Kolkata": 29, "Hyderabad": 31}.get(city, 25)
        
        for days_ago in range(7):
            for hour in range(0, 24, 3):  # Every 3 hours
                timestamp = now - timedelta(days=days_ago, hours=hour)
                # Add some random variation
                from random import uniform
                temp_variation = uniform(-3, 3)
                humidity_variation = uniform(-10, 10)
                
                sample_data.append({
                    'city': city,
                    'temperature': base_temp + temp_variation,
                    'feels_like': base_temp + temp_variation - 1,
                    'humidity': 65 + humidity_variation,
                    'wind_speed': uniform(2, 8),
                    'weather_condition': "Clear" if uniform(0, 1) > 0.3 else "Clouds",
                    'timestamp': timestamp
                })
    
    # Store in database
    result = db_handler.store_weather_data(sample_data)
    print(f"Generated and stored {len(sample_data)} sample data points")
    
    # Create daily summaries
    data_processor = DataProcessor()
    daily_summary = data_processor.calculate_daily_summary(sample_data)
    db_handler.store_daily_summary(daily_summary)
    print(f"Generated and stored {len(daily_summary)} daily summaries")
    
    db_handler.close()
    
if __name__ == "__main__":
    main()
    
    # Uncomment the line below to generate sample data for testing
    from src.data_processing.data_processor import DataProcessor
    generate_sample_data()