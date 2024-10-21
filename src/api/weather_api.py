import requests
from typing import List, Dict
import time
from src.utils.logger import logger

class WeatherAPI:
    BASE_URL = "http://api.openweathermap.org/data/2.5/"

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
                response = requests.get(f"{self.BASE_URL}weather", params=params)
                response.raise_for_status()
                data = response.json()
                weather_data.append({
                    "city": city,
                    "main": data["weather"][0]["main"],
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "dt": data["dt"]
                })
                logger.info(f"Successfully retrieved weather data for {city}")
            except requests.RequestException as e:
                logger.error(f"Error fetching data for {city}: {str(e)}")
            time.sleep(1)  # To avoid hitting rate limits
        return weather_data

    def get_forecast_data(self, cities: List[str], days: int = 5) -> Dict[str, List[Dict]]:
        forecast_data = {}
        for city in cities:
            try:
                params = {
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8  # 8 forecasts per day
                }
                response = requests.get(f"{self.BASE_URL}forecast", params=params)
                response.raise_for_status()
                data = response.json()
                forecast_data[city] = [
                    {
                        "dt": item["dt"],
                        "temp": item["main"]["temp"],
                        "main": item["weather"][0]["main"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"]
                    } for item in data["list"]
                ]
                logger.info(f"Successfully retrieved forecast data for {city}")
            except requests.RequestException as e:
                logger.error(f"Error fetching forecast data for {city}: {str(e)}")
            time.sleep(1)  # To avoid hitting rate limits
        return forecast_data