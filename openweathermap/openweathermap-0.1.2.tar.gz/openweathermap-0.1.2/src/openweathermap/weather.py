import datetime

import pytz
from django.conf import settings
import requests


class WeatherMiniInfo:
    def __init__(self, min, max, icon, date):
        self.min = min
        self.max = max
        self.icon_url = f'http://openweathermap.org/img/wn/{icon}@2x.png'
        self.date = date


class Weather:
    openweathermap_api_url = 'https://api.openweathermap.org/data/2.5/onecall?' \
                             'lat={lat}&lon={lon}&appid={token}&units=metric'

    def __init__(self, lat: float, long: float):
        self.lat = lat
        self.long = long
        self.token = settings.OPENWEATHERMAP_TOKEN
        self.data = None
        self.one_call_api_data()

    def one_call_api_data(self):
        self.data = requests.get(
            url=Weather.openweathermap_api_url.format(lat=self.lat, lon=self.long, token=self.token)).json()

    def next_seven_days_forecast(self, timezone='Europe/London'):
        daily = self.data['daily']
        forecast = []

        for i in range(8):
            forecast.append(WeatherMiniInfo(min=daily[i]['temp']['min'],
                                            max=daily[i]['temp']['max'],
                                            icon=daily[i]['weather'][0]['icon'],
                                            date=datetime.datetime.fromtimestamp(daily[i]['dt'],
                                                                                 tz=pytz.UTC).astimezone(
                                                tz=pytz.timezone(timezone))))
        return forecast
