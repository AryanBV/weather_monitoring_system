import requests
from typing import List, Dict
import time
from src.utils.logger import logger

class WeatherAPI:
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather_data(self, cities: List[str]) -> List[Dict]:
        weather_data = []
        for city in cities:
            try:
                params = {
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric"
                }
                response = requests.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                weather_data.append({
                    "city": city,
                    "main": data["weather"][0]["main"],
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "dt": data["dt"]
                })
                logger.info(f"Successfully retrieved weather data for {city}")
            except requests.RequestException as e:
                logger.error(f"Error fetching data for {city}: {str(e)}")
            time.sleep(1)  # To avoid hitting rate limits
        return weather_data