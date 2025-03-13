from pymongo import MongoClient, errors
from datetime import datetime, timedelta
import time
import os
from src.utils.logger import logger

class DBHandler:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.db = None
        self.weather_collection = None
        self.summary_collection = None
        self.forecast_collection = None
        self._connect()
        
    def _connect(self, max_retries=3):
        """Establish connection to MongoDB with retry logic"""
        retries = 0
        while retries < max_retries:
            try:
                # Check for MongoDB URI in environment variables
                mongodb_uri = os.environ.get('MONGODB_URI')
                
                if mongodb_uri:
                    # Connect using MongoDB URI from environment
                    self.client = MongoClient(mongodb_uri, 
                                             serverSelectionTimeoutMS=5000,
                                             maxPoolSize=50,
                                             connectTimeoutMS=5000,
                                             retryWrites=True,
                                             w='majority')
                    logger.info("Connecting to MongoDB using URI from environment")
                else:
                    # Fall back to connection using host and port
                    self.client = MongoClient(
                        host=self.config['host'],
                        port=self.config['port'],
                        serverSelectionTimeoutMS=5000,
                        maxPoolSize=50,
                        connectTimeoutMS=5000,
                        retryWrites=True,
                        w='majority'
                    )
                    logger.info("Connecting to MongoDB using host and port configuration")
                
                # Test the connection
                self.client.admin.command('ping')
                
                # Get database from URI or use configured name
                if mongodb_uri:
                    # Extract database name from URI or use the configured name
                    db_name = mongodb_uri.split('/')[-1].split('?')[0] or self.config['name']
                    self.db = self.client[db_name]
                else:
                    self.db = self.client[self.config['name']]
                    
                self.weather_collection = self.db['weather_data']
                self.summary_collection = self.db['daily_summaries']
                self.forecast_collection = self.db['forecast_data']
                
                # Create indexes for better query performance
                self.weather_collection.create_index([("city", 1), ("timestamp", -1)])
                self.summary_collection.create_index([("city", 1), ("date", -1)])
                self.forecast_collection.create_index([("city", 1), ("date", -1)])
                
                logger.info("Successfully connected to MongoDB")
                return
            except errors.ConnectionFailure as e:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                logger.error(f"Failed to connect to MongoDB (attempt {retries}/{max_retries}): {str(e)}")
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                
        raise ConnectionError("Failed to connect to MongoDB after multiple attempts")
    
    def _ensure_connection(self):
        """Ensure an active MongoDB connection, reconnect if necessary"""
        try:
            # Check if the connection is still alive
            self.client.admin.command('ping')
        except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError, AttributeError):
            logger.warning("MongoDB connection lost, attempting to reconnect")
            self._connect()

    def store_weather_data(self, data):
        self._ensure_connection()
        try:
            result = self.weather_collection.insert_many(data)
            logger.info(f"Stored {len(result.inserted_ids)} weather data points")
            return result.inserted_ids
        except errors.PyMongoError as e:
            logger.error(f"Error storing weather data: {str(e)}")
            return None

    def store_daily_summary(self, summaries):
        self._ensure_connection()
        try:
            result_count = 0
            for summary in summaries:
                result = self.summary_collection.update_one(
                    {'city': summary['city'], 'date': summary['date']},
                    {'$set': summary},
                    upsert=True
                )
                if result.modified_count or result.upserted_id:
                    result_count += 1
            logger.info(f"Stored/updated {result_count} daily summaries")
            return result_count
        except errors.PyMongoError as e:
            logger.error(f"Error storing daily summaries: {str(e)}")
            return 0

    def store_forecast_summary(self, forecast_summaries):
        self._ensure_connection()
        try:
            result_count = 0
            for city, summaries in forecast_summaries.items():
                for summary in summaries:
                    result = self.forecast_collection.update_one(
                        {'city': city, 'date': summary['date']},
                        {'$set': summary},
                        upsert=True
                    )
                    if result.modified_count or result.upserted_id:
                        result_count += 1
            logger.info(f"Stored/updated {result_count} forecast summaries")
            return result_count
        except errors.PyMongoError as e:
            logger.error(f"Error storing forecast summaries: {str(e)}")
            return 0

    def get_recent_weather_data(self, city, limit=10):
        self._ensure_connection()
        try:
            return list(self.weather_collection.find(
                {'city': city},
                sort=[('timestamp', -1)],
                limit=limit
            ))
        except errors.PyMongoError as e:
            logger.error(f"Error retrieving recent weather data for {city}: {str(e)}")
            return []

    def get_daily_summaries(self, city, start_date, end_date):
        self._ensure_connection()
        try:
            return list(self.summary_collection.find({
                'city': city,
                'date': {'$gte': start_date, '$lte': end_date}
            }))
        except errors.PyMongoError as e:
            logger.error(f"Error retrieving daily summaries for {city}: {str(e)}")
            return []

    def get_forecast_data(self, city, start_date, end_date):
        self._ensure_connection()
        try:
            return list(self.forecast_collection.find({
                'city': city,
                'date': {'$gte': start_date, '$lte': end_date}
            }))
        except errors.PyMongoError as e:
            logger.error(f"Error retrieving forecast data for {city}: {str(e)}")
            return []

    def get_cities(self):
        self._ensure_connection()
        try:
            return self.weather_collection.distinct('city')
        except errors.PyMongoError as e:
            logger.error(f"Error retrieving city list: {str(e)}")
            return []

    def get_data_for_alerts(self, city, hours=24):
        self._ensure_connection()
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            return list(self.weather_collection.find({
                'city': city,
                'timestamp': {'$gte': start_time}
            }).sort('timestamp', 1))
        except errors.PyMongoError as e:
            logger.error(f"Error retrieving alert data for {city}: {str(e)}")
            return []
    
    def get_historical_weather_data(self, city, days=30):
        self._ensure_connection()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            return list(self.weather_collection.find({
                'city': city,
                'timestamp': {'$gte': start_date}
            }).sort('timestamp', 1))
        except errors.PyMongoError as e:
            logger.error(f"Error retrieving historical data for {city}: {str(e)}")
            return []

    def close(self):
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB connection closed")
            except:
                pass