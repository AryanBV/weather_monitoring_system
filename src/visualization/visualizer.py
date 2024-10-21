import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

class Visualizer:
    def __init__(self):
        self.output_dir = 'visualizations'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def update_visualizations(self, daily_summaries, alerts):
        self.plot_temperature_trends(daily_summaries)
        self.plot_weather_conditions(daily_summaries)
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