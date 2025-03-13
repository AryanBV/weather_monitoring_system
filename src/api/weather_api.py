import requests
from typing import List, Dict, Optional
import time
import random
from src.utils.logger import logger

class WeatherAPI:
    BASE_URL = "http://api.openweathermap.org/data/2.5/"
    MAX_RETRIES = 3

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache = {}  # Simple in-memory cache
        self.cache_expiry = 300  # Cache duration in seconds

    def _make_request_with_retry(self, url: str, params: Dict) -> Optional[Dict]:
        """Make an API request with exponential backoff retry logic"""
        retry_count = 0
        while retry_count < self.MAX_RETRIES:
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                retry_count += 1
                if retry_count == self.MAX_RETRIES:
                    logger.error(f"Failed after {self.MAX_RETRIES} retries: {str(e)}")
                    return None
                
                # Calculate exponential backoff with jitter
                wait_time = (2 ** retry_count) + random.uniform(0, 1)
                logger.warning(f"Request failed: {str(e)}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        return None  # This line should not be reached due to the return in the exception handling

    def get_weather_data(self, cities: List[str]) -> List[Dict]:
        """Get current weather data for multiple cities with caching"""
        weather_data = []
        current_time = time.time()
        
        for city in cities:
            cache_key = f"current_{city}"
            # Check cache first
            if cache_key in self.cache and current_time - self.cache[cache_key]['timestamp'] < self.cache_expiry:
                logger.info(f"Using cached weather data for {city}")
                weather_data.append(self.cache[cache_key]['data'])
                continue
                
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            data = self._make_request_with_retry(f"{self.BASE_URL}weather", params)
            
            if data:
                processed_data = {
                    "city": city,
                    "main": data["weather"][0]["main"],
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "dt": data["dt"]
                }
                
                # Save to cache
                self.cache[cache_key] = {
                    'data': processed_data,
                    'timestamp': current_time
                }
                
                weather_data.append(processed_data)
                logger.info(f"Successfully retrieved weather data for {city}")
            else:
                logger.error(f"Failed to retrieve weather data for {city}")
            
            time.sleep(1)  # To avoid hitting rate limits
            
        return weather_data

    def get_forecast_data(self, cities: List[str], days: int = 5) -> Dict[str, List[Dict]]:
        """Get forecast data for multiple cities with caching"""
        forecast_data = {}
        current_time = time.time()
        
        for city in cities:
            cache_key = f"forecast_{city}_{days}"
            # Check cache first
            if cache_key in self.cache and current_time - self.cache[cache_key]['timestamp'] < self.cache_expiry:
                logger.info(f"Using cached forecast data for {city}")
                forecast_data[city] = self.cache[cache_key]['data']
                continue
            
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day
            }
            
            data = self._make_request_with_retry(f"{self.BASE_URL}forecast", params)
            
            if data:
                city_forecast = [
                    {
                        "dt": item["dt"],
                        "temp": item["main"]["temp"],
                        "main": item["weather"][0]["main"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"]
                    } for item in data["list"]
                ]
                
                # Save to cache
                self.cache[cache_key] = {
                    'data': city_forecast,
                    'timestamp': current_time
                }
                
                forecast_data[city] = city_forecast
                logger.info(f"Successfully retrieved forecast data for {city}")
            else:
                logger.error(f"Failed to retrieve forecast data for {city}")
                
            time.sleep(1)  # To avoid hitting rate limits
            
        return forecast_data

    def clear_cache(self):
        """Clear the API cache"""
        self.cache = {}
        logger.info("API cache cleared")