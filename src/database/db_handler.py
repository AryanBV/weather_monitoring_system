from pymongo import MongoClient
from datetime import datetime, timedelta

class DBHandler:
    def __init__(self, config):
        self.client = MongoClient(config['host'], config['port'])
        self.db = self.client[config['name']]
        self.weather_collection = self.db['weather_data']
        self.summary_collection = self.db['daily_summaries']
        self.forecast_collection = self.db['forecast_data']

    def store_weather_data(self, data):
        for item in data:
            self.weather_collection.insert_one(item)

    def store_daily_summary(self, summaries):
        for summary in summaries:
            self.summary_collection.update_one(
                {'city': summary['city'], 'date': summary['date']},
                {'$set': summary},
                upsert=True
            )

    def store_forecast_summary(self, forecast_summaries):
        for city, summaries in forecast_summaries.items():
            for summary in summaries:
                self.forecast_collection.update_one(
                    {'city': city, 'date': summary['date']},
                    {'$set': summary},
                    upsert=True
                )

    def get_recent_weather_data(self, city, limit=10):
        return list(self.weather_collection.find(
            {'city': city},
            sort=[('timestamp', -1)],
            limit=limit
        ))

    def get_daily_summaries(self, city, start_date, end_date):
        return list(self.summary_collection.find({
            'city': city,
            'date': {'$gte': start_date, '$lte': end_date}
        }))

    def get_forecast_data(self, city, start_date, end_date):
        return list(self.forecast_collection.find({
            'city': city,
            'date': {'$gte': start_date, '$lte': end_date}
        }))

    def get_cities(self):
        return self.weather_collection.distinct('city')

    def get_data_for_alerts(self, city, hours=24):
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return list(self.weather_collection.find({
            'city': city,
            'timestamp': {'$gte': start_time}
        }).sort('timestamp', 1))
    
    def get_historical_weather_data(self, city, days=30):
        start_date = datetime.utcnow() - timedelta(days=days)
        return list(self.weather_collection.find({
            'city': city,
            'timestamp': {'$gte': start_date}
        }).sort('timestamp', 1))

    def close(self):
        self.client.close()