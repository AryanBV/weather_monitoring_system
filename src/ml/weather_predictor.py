import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class WeatherPredictor:
    def __init__(self, city):
        self.city = city
        self.model = None
        self.le = LabelEncoder()
        self.model_path = f'models/{city}_weather_model.joblib'

    def prepare_data(self, data):
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['weather_condition'] = self.le.fit_transform(df['weather_condition'])
        return df

    def train_model(self, data):
        df = self.prepare_data(data)
        X = df[['hour', 'day_of_week', 'month', 'humidity', 'wind_speed', 'weather_condition']]
        y = df['temperature']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        self.save_model()

    def predict(self, hour, day_of_week, month, humidity, wind_speed, weather_condition):
        if self.model is None:
            self.load_model()
        weather_condition_encoded = self.le.transform([weather_condition])[0]
        prediction = self.model.predict([[hour, day_of_week, month, humidity, wind_speed, weather_condition_encoded]])
        return prediction[0]

    def save_model(self):
        if not os.path.exists('models'):
            os.makedirs('models')
        joblib.dump(self.model, self.model_path)

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            raise FileNotFoundError(f"No trained model found for {self.city}")