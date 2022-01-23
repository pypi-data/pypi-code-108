from datetime import datetime
from typing import List
import re


def convertCamelCase(nameArray):
    data = {}

    for key in nameArray:
        data[re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()] = nameArray[key]

    return data


class Current:
    time: str
    symbol: str
    symbol_phrase: str
    temperature: int
    feels_like_temp: int
    rel_humidity: int
    dew_point: int
    wind_speed: int
    wind_dir_string: str
    wind_gust: int
    precip_prob: int
    precip_rate: None
    cloudiness: int
    thunder_prob: int
    uv_index: int
    pressure: float
    visibility: int

    def __init__(self, time: str, symbol: str, symbol_phrase: str, temperature: int, feels_like_temp: int,
                 rel_humidity: int, dew_point: int, wind_speed: int, wind_dir_string: str, wind_gust: int,
                 precip_prob: int, precip_rate: None, cloudiness: int, thunder_prob: int, uv_index: int,
                 pressure: float, visibility: int) -> None:
        self.time = time
        self.symbol = symbol
        self.symbol_phrase = symbol_phrase
        self.temperature = temperature
        self.feels_like_temp = feels_like_temp
        self.rel_humidity = rel_humidity
        self.dew_point = dew_point
        self.wind_speed = wind_speed
        self.wind_dir_string = wind_dir_string
        self.wind_gust = wind_gust
        self.precip_prob = precip_prob
        self.precip_rate = precip_rate
        self.cloudiness = cloudiness
        self.thunder_prob = thunder_prob
        self.uv_index = uv_index
        self.pressure = pressure
        self.visibility = visibility


class Daily:
    date: datetime
    symbol: str
    symbol_phrase: str
    max_temp: int
    min_temp: int
    max_feels_like_temp: int
    min_feels_like_temp: int
    max_rel_humidity: int
    min_rel_humidity: int
    max_dew_point: int
    min_dew_point: int
    precip_accum: int
    max_wind_speed: int
    wind_dir: int
    max_wind_gust: int
    precip_prob: int
    cloudiness: int
    sunrise: datetime
    sunset: datetime
    sunrise_epoch: int
    sunset_epoch: int
    moonrise: datetime
    moonset: datetime
    moon_phase: int
    uv_index: int
    min_visibility: int
    pressure: float

    def __init__(self, date: datetime, symbol: str, symbol_phrase: str, max_temp: int, min_temp: int,
                 max_feels_like_temp: int, min_feels_like_temp: int, max_rel_humidity: int, min_rel_humidity: int,
                 max_dew_point: int, min_dew_point: int, precip_accum: int, max_wind_speed: int, wind_dir: int,
                 max_wind_gust: int, precip_prob: int, cloudiness: int, sunrise: datetime, sunset: datetime,
                 sunrise_epoch: int, sunset_epoch: int, moonrise: datetime, moonset: datetime, moon_phase: int,
                 uv_index: int, min_visibility: int, pressure: float) -> None:
        self.date = date
        self.symbol = symbol
        self.symbol_phrase = symbol_phrase
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.max_feels_like_temp = max_feels_like_temp
        self.min_feels_like_temp = min_feels_like_temp
        self.max_rel_humidity = max_rel_humidity
        self.min_rel_humidity = min_rel_humidity
        self.max_dew_point = max_dew_point
        self.min_dew_point = min_dew_point
        self.precip_accum = precip_accum
        self.max_wind_speed = max_wind_speed
        self.wind_dir = wind_dir
        self.max_wind_gust = max_wind_gust
        self.precip_prob = precip_prob
        self.cloudiness = cloudiness
        self.sunrise = sunrise
        self.sunset = sunset
        self.sunrise_epoch = sunrise_epoch
        self.sunset_epoch = sunset_epoch
        self.moonrise = moonrise
        self.moonset = moonset
        self.moon_phase = moon_phase
        self.uv_index = uv_index
        self.min_visibility = min_visibility
        self.pressure = pressure


class Weather:
    daily: List[Daily] = []
    hourly: List[Current] = []
    current: Current

    def __init__(self, daily: List[Daily], hourly: List[Current], current: Current) -> None:
        self.daily = []
        for param in daily:
            param = convertCamelCase(param)
            self.daily.append(Daily(**dict(param)))

        self.hourly = []
        for param in hourly:
            param = convertCamelCase(param)
            self.hourly.append(Current(**dict(param)))

        current = convertCamelCase(current)
        self.current = Current(**dict(current))


class WeatherData:
    data: Weather = []

    def __init__(self, data) -> None:
        self.data = Weather(**dict(data))

    def getDataOnTypeHourly(self, typeWeather):
        if typeWeather == 'time':
            return self.data.current.time
        elif typeWeather == 'temperature':
            return self.data.current.temperature
        elif typeWeather == 'feels_like_temp':
            return self.data.current.feels_like_temp
        elif typeWeather == 'rel_humidity':
            return self.data.current.rel_humidity
        elif typeWeather == 'dew_point':
            return self.data.current.dew_point
        elif typeWeather == 'wind_speed':
            return self.data.current.wind_speed
        elif typeWeather == 'wind_dir_string':
            return self.data.current.wind_dir_string
        elif typeWeather == 'wind_gust':
            return self.data.current.wind_gust
        elif typeWeather == 'precip_prob':
            return self.data.current.precip_prob
        elif typeWeather == 'precip_rate':
            return self.data.current.precip_rate
        elif typeWeather == 'cloudiness':
            return self.data.current.cloudiness
        elif typeWeather == 'thunder_prob':
            return self.data.current.thunder_prob
        elif typeWeather == 'uv_index':
            return self.data.current.uv_index
        elif typeWeather == 'pressure':
            return self.data.current.pressure
        elif typeWeather == 'visibility':
            return self.data.current.visibility
        else:
            return 0
