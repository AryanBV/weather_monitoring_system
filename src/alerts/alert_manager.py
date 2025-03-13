from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from src.utils.logger import logger

class AlertManager:
    def __init__(self, thresholds):
        self.high_temp_threshold = thresholds['high_temperature']
        self.low_temp_threshold = thresholds['low_temperature']
        self.consecutive_updates = thresholds['consecutive_updates']
        self.alert_history = {}
        
        # Email configuration - should be set via environment variables
        self.email_enabled = os.environ.get('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('ALERT_FROM_EMAIL', '')
        self.to_emails = os.environ.get('ALERT_TO_EMAILS', '').split(',')
        
        if self.email_enabled and (not self.smtp_username or not self.smtp_password):
            logger.warning("Email alerts enabled but SMTP credentials not configured properly")

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
        # Always log the alerts
        for alert in alerts:
            alert_msg = f"ALERT: {alert['type']} alert for {alert['city']}: {alert['temperature']}°C at {alert['timestamp']}"
            logger.warning(alert_msg)
        
        # Send email alerts if enabled
        if self.email_enabled and alerts and self.to_emails:
            try:
                self._send_email_alert(alerts)
            except Exception as e:
                logger.error(f"Failed to send email alerts: {str(e)}")
    
    def _send_email_alert(self, alerts):
        """Send email notifications for alerts"""
        if not self.email_enabled or not alerts:
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)
        msg['Subject'] = f"Weather Alert: {len(alerts)} new weather condition alerts"
        
        # Build email body
        body = "The following weather alerts have been triggered:\n\n"
        for alert in alerts:
            body += f"- {alert['city']}: {alert['type']} alert at {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}, temperature: {alert['temperature']}°C\n"
        
        body += "\n\nThis is an automated message from your Weather Monitoring System."
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email alert sent to {', '.join(self.to_emails)}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise