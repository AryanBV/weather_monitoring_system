from src.database.db_handler import DBHandler
from src.data_processing.data_processor import DataProcessor
from src.utils.config_loader import load_config
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def generate_sample_data():
    """Generate sample historical data for testing purposes"""
    print("Generating sample historical weather data...")
    
    config = load_config()
    db_handler = DBHandler(config['database'])
    data_processor = DataProcessor()
    
    cities = config['cities']
    print(f"Generating sample data for {len(cities)} cities...")
    
    # Create 7 days of historical data
    sample_data = []
    now = datetime.now()
    
    # Base temperatures for different cities (approximate average temperatures)
    base_temps = {
        "Delhi": 28, 
        "Mumbai": 30, 
        "Chennai": 32, 
        "Bangalore": 26, 
        "Kolkata": 29, 
        "Hyderabad": 31
    }
    
    # Weather patterns (more realistic conditions for each city)
    weather_patterns = {
        "Delhi": ["Clear", "Haze", "Clouds"],
        "Mumbai": ["Clouds", "Clear", "Rain"],
        "Chennai": ["Clear", "Clouds", "Rain"],
        "Bangalore": ["Clouds", "Clear", "Rain"],
        "Kolkata": ["Clouds", "Haze", "Clear"],
        "Hyderabad": ["Clear", "Clouds"]
    }
    
    for city in cities:
        base_temp = base_temps.get(city, 25)
        possible_conditions = weather_patterns.get(city, ["Clear", "Clouds"])
        
        print(f"Generating data for {city}...")
        
        # Generate data points for the past 7 days
        for days_ago in range(7):
            # Create a slight daily pattern (cooler at night, warmer in day)
            for hour in range(0, 24, 3):  # Every 3 hours
                timestamp = now - timedelta(days=days_ago, hours=hour)
                
                # Add some temperature variation 
                # Warmer in the day (6am-6pm), cooler at night
                hour_of_day = timestamp.hour
                day_factor = 3 if 6 <= hour_of_day <= 18 else -2
                
                # Add random variation
                temp_variation = random.uniform(-2, 2) + day_factor
                humidity_variation = random.uniform(-10, 10)
                
                # Determine weather condition (more likely to be clear during the day)
                weather_condition = random.choice(possible_conditions)
                
                sample_data.append({
                    'city': city,
                    'temperature': base_temp + temp_variation,
                    'feels_like': base_temp + temp_variation - 1,
                    'humidity': 65 + humidity_variation,
                    'wind_speed': random.uniform(2, 8),
                    'weather_condition': weather_condition,
                    'timestamp': timestamp
                })
    
    # Store in database
    if sample_data:
        result = db_handler.store_weather_data(sample_data)
        print(f"Generated and stored {len(sample_data)} sample data points")
        
        # Create daily summaries
        daily_summary = data_processor.calculate_daily_summary(sample_data)
        db_handler.store_daily_summary(daily_summary)
        print(f"Generated and stored {len(daily_summary)} daily summaries")
    else:
        print("No sample data was generated!")
    
    db_handler.close()
    print("Done!")

if __name__ == "__main__":
    generate_sample_data()