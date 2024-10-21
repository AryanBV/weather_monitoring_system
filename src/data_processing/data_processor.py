from datetime import datetime
from collections import defaultdict

class DataProcessor:
    def process(self, raw_data):
        processed_data = []
        for item in raw_data:
            processed_item = {
                'city': item['city'],
                'temperature': item['temp'],
                'feels_like': item['feels_like'],
                'humidity': item['humidity'],
                'wind_speed': item['wind_speed'],
                'weather_condition': item['main'],
                'timestamp': datetime.fromtimestamp(item['dt']),
            }
            processed_data.append(processed_item)
        return processed_data

    def calculate_daily_summary(self, data):
        summaries = {}
        for item in data:
            date = item['timestamp'].date()
            city = item['city']
            key = (city, date)
            
            if key not in summaries:
                summaries[key] = {
                    'city': city,
                    'date': datetime.combine(date, datetime.min.time()),  # Convert to datetime
                    'temp_sum': 0,
                    'humidity_sum': 0,
                    'wind_speed_sum': 0,
                    'temp_count': 0,
                    'max_temp': float('-inf'),
                    'min_temp': float('inf'),
                    'conditions': {}
                }
            
            summary = summaries[key]
            summary['temp_sum'] += item['temperature']
            summary['humidity_sum'] += item['humidity']
            summary['wind_speed_sum'] += item['wind_speed']
            summary['temp_count'] += 1
            summary['max_temp'] = max(summary['max_temp'], item['temperature'])
            summary['min_temp'] = min(summary['min_temp'], item['temperature'])
            
            condition = item['weather_condition']
            summary['conditions'][condition] = summary['conditions'].get(condition, 0) + 1

        result = []
        for key, summary in summaries.items():
            avg_temp = summary['temp_sum'] / summary['temp_count']
            avg_humidity = summary['humidity_sum'] / summary['temp_count']
            avg_wind_speed = summary['wind_speed_sum'] / summary['temp_count']
            dominant_condition = max(summary['conditions'], key=summary['conditions'].get)
            
            result.append({
                'city': summary['city'],
                'date': summary['date'],
                'avg_temperature': round(avg_temp, 2),
                'max_temperature': round(summary['max_temp'], 2),
                'min_temperature': round(summary['min_temp'], 2),
                'avg_humidity': round(avg_humidity, 2),
                'avg_wind_speed': round(avg_wind_speed, 2),
                'dominant_condition': dominant_condition
            })

        return result

    def process_forecast(self, forecast_data):
        processed_forecast = defaultdict(list)
        for city, forecasts in forecast_data.items():
            for forecast in forecasts:
                processed_forecast[city].append({
                    'timestamp': datetime.fromtimestamp(forecast['dt']),
                    'temperature': forecast['temp'],
                    'humidity': forecast['humidity'],
                    'wind_speed': forecast['wind_speed'],
                    'weather_condition': forecast['main']
                })
        return processed_forecast

    def summarize_forecast(self, processed_forecast):
        summary = {}
        for city, forecasts in processed_forecast.items():
            city_summary = defaultdict(lambda: {'temps': [], 'humidity': [], 'wind_speed': [], 'conditions': []})
            for forecast in forecasts:
                date = forecast['timestamp'].date()
                city_summary[date]['temps'].append(forecast['temperature'])
                city_summary[date]['humidity'].append(forecast['humidity'])
                city_summary[date]['wind_speed'].append(forecast['wind_speed'])
                city_summary[date]['conditions'].append(forecast['weather_condition'])
            
            summary[city] = [
                {
                    'date': datetime.combine(date, datetime.min.time()),  # Convert to datetime
                    'avg_temp': sum(data['temps']) / len(data['temps']),
                    'max_temp': max(data['temps']),
                    'min_temp': min(data['temps']),
                    'avg_humidity': sum(data['humidity']) / len(data['humidity']),
                    'avg_wind_speed': sum(data['wind_speed']) / len(data['wind_speed']),
                    'dominant_condition': max(set(data['conditions']), key=data['conditions'].count)
                } for date, data in city_summary.items()
            ]
        return summary