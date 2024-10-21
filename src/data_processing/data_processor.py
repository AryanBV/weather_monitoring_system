from datetime import datetime

class DataProcessor:
    def __init__(self):
        pass

    def process(self, raw_data):
        processed_data = []
        for item in raw_data:
            processed_item = {
                'city': item['city'],
                'temperature': item['temp'],
                'feels_like': item['feels_like'],
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
                    'temp_count': 0,
                    'max_temp': float('-inf'),
                    'min_temp': float('inf'),
                    'conditions': {}
                }
            
            summary = summaries[key]
            summary['temp_sum'] += item['temperature']
            summary['temp_count'] += 1
            summary['max_temp'] = max(summary['max_temp'], item['temperature'])
            summary['min_temp'] = min(summary['min_temp'], item['temperature'])
            
            condition = item['weather_condition']
            summary['conditions'][condition] = summary['conditions'].get(condition, 0) + 1

        result = []
        for key, summary in summaries.items():
            avg_temp = summary['temp_sum'] / summary['temp_count']
            dominant_condition = max(summary['conditions'], key=summary['conditions'].get)
            
            result.append({
                'city': summary['city'],
                'date': summary['date'],
                'avg_temperature': round(avg_temp, 2),
                'max_temperature': round(summary['max_temp'], 2),
                'min_temperature': round(summary['min_temp'], 2),
                'dominant_condition': dominant_condition
            })

        return result