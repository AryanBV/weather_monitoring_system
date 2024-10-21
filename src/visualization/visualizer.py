import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

class Visualizer:
    def __init__(self):
        self.output_dir = 'visualizations'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def update_visualizations(self, daily_summaries, forecast_summaries, alerts):
        self.plot_temperature_trends(daily_summaries)
        self.plot_weather_conditions(daily_summaries)
        self.plot_humidity_wind(daily_summaries)
        self.plot_forecast(forecast_summaries)
        self.plot_alerts(alerts)

    def plot_temperature_trends(self, daily_summaries):
        plt.figure(figsize=(12, 6))
        
        cities = set(summary['city'] for summary in daily_summaries)
        for city in cities:
            city_data = [s for s in daily_summaries if s['city'] == city]
            dates = [s['date'] for s in city_data]
            avg_temps = [s['avg_temperature'] for s in city_data]
            plt.plot(dates, avg_temps, label=city, marker='o')

        plt.title('Average Temperature Trends')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.grid(True)
        
        filename = f'temperature_trends_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()

    def plot_weather_conditions(self, daily_summaries):
        plt.figure(figsize=(12, 6))
        
        conditions = {}
        for summary in daily_summaries:
            city = summary['city']
            condition = summary['dominant_condition']
            if city not in conditions:
                conditions[city] = {}
            conditions[city][condition] = conditions[city].get(condition, 0) + 1

        cities = list(conditions.keys())
        bottom = [0] * len(cities)

        for condition in set.union(*[set(city_conditions.keys()) for city_conditions in conditions.values()]):
            values = [conditions[city].get(condition, 0) for city in cities]
            plt.bar(cities, values, bottom=bottom, label=condition)
            bottom = [b + v for b, v in zip(bottom, values)]

        plt.title('Dominant Weather Conditions')
        plt.xlabel('City')
        plt.ylabel('Number of Days')
        plt.legend()
        
        filename = f'weather_conditions_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()

    def plot_humidity_wind(self, daily_summaries):
        plt.figure(figsize=(12, 6))
        
        cities = list(set(summary['city'] for summary in daily_summaries))
        cities.sort()  # Sort cities for consistent ordering
        
        humidity_data = []
        wind_speed_data = []
        
        for city in cities:
            city_data = [s for s in daily_summaries if s['city'] == city]
            humidity = [s['avg_humidity'] for s in city_data]
            wind_speed = [s['avg_wind_speed'] for s in city_data]
            
            print(f"Debug - {city}:")
            print(f"Humidity: {humidity}")
            print(f"Wind Speed: {wind_speed}")
            
            humidity_data.append(humidity[-1] if humidity else 0)  # Use the latest data point
            wind_speed_data.append(wind_speed[-1] if wind_speed else 0)  # Use the latest data point

        x = range(len(cities))
        width = 0.35

        plt.bar([i - width/2 for i in x], humidity_data, width, label='Humidity (%)', alpha=0.8)
        plt.bar([i + width/2 for i in x], wind_speed_data, width, label='Wind Speed (m/s)', alpha=0.8)

        plt.xlabel('City')
        plt.ylabel('Value')
        plt.title('Latest Humidity and Wind Speed by City')
        plt.xticks(x, cities, rotation=45)
        plt.legend()

        plt.tight_layout()
        filename = f'humidity_wind_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()

    def plot_forecast(self, forecast_summaries):
        plt.figure(figsize=(12, 6))
        
        for city, forecasts in forecast_summaries.items():
            dates = [f['date'] for f in forecasts]
            temps = [f['avg_temp'] for f in forecasts]
            plt.plot(dates, temps, label=city, marker='o')

        plt.title('5-Day Temperature Forecast')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.grid(True)
        
        filename = f'temperature_forecast_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()

    def plot_alerts(self, alerts):
        plt.figure(figsize=(12, 6))
        
        cities = set(alert['city'] for alert in alerts)
        for city in cities:
            city_alerts = [alert for alert in alerts if alert['city'] == city]
            times = [alert['timestamp'] for alert in city_alerts]
            temperatures = [alert['temperature'] for alert in city_alerts]
            plt.scatter(times, temperatures, label=city, marker='o')

        plt.title('Temperature Alerts')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.grid(True)
        
        filename = f'temperature_alerts_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()