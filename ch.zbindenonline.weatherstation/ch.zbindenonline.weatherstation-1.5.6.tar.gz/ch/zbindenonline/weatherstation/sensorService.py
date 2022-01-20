import datetime
import logging
from typing import List

from tinkerforge.bricklet_outdoor_weather import BrickletOutdoorWeather
from tinkerforge.ip_connection import IPConnection

from ch.zbindenonline.weatherstation.domain import Measure


class SensorService:
    def __init__(self, outdoor_weather_uid: str, host: str = 'localhost', port: int = 4223):
        self.uid = outdoor_weather_uid
        self.host = host
        self.port = port

    def get_measures(self) -> List[Measure]:
        ip_connection = self.create_ip_connection()
        ow = self.create_ow_bricklet(ip_connection)

        ip_connection.connect(self.host, self.port)
        try:
            result = []
            sensor_ids = ow.get_sensor_identifiers()
            for sensor_id in sensor_ids:
                sensor_data = ow.get_sensor_data(sensor_id)
                if sensor_data.last_change >= 1200:
                    logging.debug('Measure was done ' + str(sensor_data.last_change) + 'sec ago, we ignore it')
                    continue
                measured_at = self.get_now() - datetime.timedelta(0, sensor_data.last_change)
                measure = Measure(sensor_id, measured_at, sensor_data.temperature / 10, sensor_data.humidity)
                result.append(measure)
            return result
        finally:
            ip_connection.disconnect()

    def get_now(self) -> datetime:
        return datetime.datetime.now()

    def create_ow_bricklet(self, ip_connection) -> BrickletOutdoorWeather:
        return BrickletOutdoorWeather(self.uid, ip_connection)

    def create_ip_connection(self) -> IPConnection:
        return IPConnection()
