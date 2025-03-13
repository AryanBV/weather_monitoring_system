import unittest
import os
from unittest.mock import patch, MagicMock
from src.api.weather_api import WeatherAPI

class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test API key
        self.test_api_key = "test_api_key"
        # Create an instance of WeatherAPI with the test key
        self.api = WeatherAPI(self.test_api_key)
        # Test cities
        self.test_cities = ["TestCity1", "TestCity2"]

    @patch('src.api.weather_api.requests.get')
    def test_get_weather_data(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "weather": [{"main": "Clear"}],
            "main": {
                "temp": 25.5,
                "feels_like": 26.0,
                "humidity": 65
            },
            "wind": {"speed": 4.2},
            "dt": 1609459200  # Some Unix timestamp
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_weather_data(["TestCity"])

        # Check that the API was called with correct parameters
        mock_get.assert_called_with(
            "http://api.openweathermap.org/data/2.5/weather",
            params={
                "q": "TestCity",
                "appid": self.test_api_key,
                "units": "metric"
            },
            timeout=10
        )

        # Check the returned data structure
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["city"], "TestCity")
        self.assertEqual(result[0]["main"], "Clear")
        self.assertEqual(result[0]["temp"], 25.5)
        self.assertEqual(result[0]["feels_like"], 26.0)
        self.assertEqual(result[0]["humidity"], 65)
        self.assertEqual(result[0]["wind_speed"], 4.2)
        self.assertEqual(result[0]["dt"], 1609459200)

    @patch('src.api.weather_api.requests.get')
    def test_get_forecast_data(self, mock_get):
        # Mock the response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "list": [
                {
                    "dt": 1609459200,
                    "main": {
                        "temp": 25.5,
                        "humidity": 65
                    },
                    "weather": [{"main": "Clear"}],
                    "wind": {"speed": 4.2}
                },
                {
                    "dt": 1609470000,
                    "main": {
                        "temp": 26.5,
                        "humidity": 60
                    },
                    "weather": [{"main": "Clouds"}],
                    "wind": {"speed": 3.8}
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_forecast_data(["TestCity"], days=1)

        # Check the API was called correctly
        mock_get.assert_called_with(
            "http://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": "TestCity",
                "appid": self.test_api_key,
                "units": "metric",
                "cnt": 8  # 8 forecasts for 1 day
            },
            timeout=10
        )

        # Check the returned data structure
        self.assertIn("TestCity", result)
        self.assertEqual(len(result["TestCity"]), 2)
        self.assertEqual(result["TestCity"][0]["dt"], 1609459200)
        self.assertEqual(result["TestCity"][0]["temp"], 25.5)
        self.assertEqual(result["TestCity"][0]["main"], "Clear")
        self.assertEqual(result["TestCity"][1]["main"], "Clouds")

    def test_clear_cache(self):
        # First, add some items to the cache
        self.api.cache = {
            "test_key1": {"data": "test_data", "timestamp": 12345},
            "test_key2": {"data": "test_data2", "timestamp": 67890}
        }
        
        # Call clear_cache
        self.api.clear_cache()
        
        # Check that the cache is now empty
        self.assertEqual(self.api.cache, {})

if __name__ == '__main__':
    unittest.main()