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
        self.le_path = f'models/{city}_label_encoder.joblib'
        self.is_fitted = False

    def prepare_data(self, data):
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        self.le.fit(df['weather_condition'])
        df['weather_condition'] = self.le.transform(df['weather_condition'])
        return df

    def train_model(self, data):
        df = self.prepare_data(data)
        X = df[['hour', 'day_of_week', 'month', 'humidity', 'wind_speed', 'weather_condition']]
        y = df['temperature']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        self.save_model()
        self.is_fitted = True

    def predict(self, hour, day_of_week, month, humidity, wind_speed, weather_condition):
        if not self.is_fitted:
            self.load_model()
        try:
            weather_condition_encoded = self.le.transform([weather_condition])[0]
        except ValueError:
            # If the weather condition is not in the encoder, use a default value
            weather_condition_encoded = -1
        
        if self.model is None:
            raise ValueError("Model not trained or loaded. Please train the model first.")
        
        prediction = self.model.predict([[hour, day_of_week, month, humidity, wind_speed, weather_condition_encoded]])
        return prediction[0]

    def save_model(self):
        if not os.path.exists('models'):
            os.makedirs('models')
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.le, self.le_path)

    def load_model(self):
        if os.path.exists(self.model_path) and os.path.exists(self.le_path):
            self.model = joblib.load(self.model_path)
            self.le = joblib.load(self.le_path)
            self.is_fitted = True
        else:
            raise FileNotFoundError(f"No trained model found for {self.city}")