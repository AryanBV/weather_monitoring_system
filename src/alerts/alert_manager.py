from datetime import datetime, timedelta

class AlertManager:
    def __init__(self, thresholds):
        self.high_temp_threshold = thresholds['high_temperature']
        self.low_temp_threshold = thresholds['low_temperature']
        self.consecutive_updates = thresholds['consecutive_updates']
        self.alert_history = {}

    def check_thresholds(self, weather_data):
        alerts = []
        for data in weather_data:
            city = data['city']
            temp = data['temperature']
            timestamp = data['timestamp']

            if city not in self.alert_history:
                self.alert_history[city] = {'high': [], 'low': []}

            # Check high temperature
            if temp > self.high_temp_threshold:
                self.alert_history[city]['high'].append(timestamp)
                if len(self.alert_history[city]['high']) >= self.consecutive_updates:
                    if self._check_consecutive(self.alert_history[city]['high']):
                        alerts.append({
                            'city': city,
                            'type': 'high_temperature',
                            'temperature': temp,
                            'timestamp': timestamp
                        })
                        self.alert_history[city]['high'] = []
            else:
                self.alert_history[city]['high'] = []

            # Check low temperature
            if temp < self.low_temp_threshold:
                self.alert_history[city]['low'].append(timestamp)
                if len(self.alert_history[city]['low']) >= self.consecutive_updates:
                    if self._check_consecutive(self.alert_history[city]['low']):
                        alerts.append({
                            'city': city,
                            'type': 'low_temperature',
                            'temperature': temp,
                            'timestamp': timestamp
                        })
                        self.alert_history[city]['low'] = []
            else:
                self.alert_history[city]['low'] = []

        return alerts

    def _check_consecutive(self, timestamps):
        if len(timestamps) < self.consecutive_updates:
            return False
        
        for i in range(1, len(timestamps)):
            if timestamps[i] - timestamps[i-1] > timedelta(minutes=10):  # Assuming updates every 5 minutes
                return False
        return True

    def send_alerts(self, alerts):
        # In a real-world scenario, this method would send emails, SMS, or push notifications
        # For now, we'll just print the alerts
        for alert in alerts:
            print(f"ALERT: {alert['type']} alert for {alert['city']}: {alert['temperature']}°C at {alert['timestamp']}")