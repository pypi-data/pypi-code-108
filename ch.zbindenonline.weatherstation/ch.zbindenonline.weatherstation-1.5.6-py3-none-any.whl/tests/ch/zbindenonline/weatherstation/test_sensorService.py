import unittest
from datetime import datetime

from mockito import mock, when
from tinkerforge.bricklet_outdoor_weather import BrickletOutdoorWeather
from tinkerforge.ip_connection import IPConnection

from ch.zbindenonline.weatherstation.sensorService import SensorService


class TestSensorService(SensorService):
    def __init__(self, outdoor_weather_uid, host, port, ip_conection: IPConnection,
                 ow_bricklet: BrickletOutdoorWeather, now: datetime = datetime.now()):
        super().__init__(outdoor_weather_uid, host, port)
        self.ip_connection = ip_conection
        self.ow_bricklet = ow_bricklet
        self.now = now

    def create_ip_connection(self) -> IPConnection:
        return self.ip_connection

    def create_ow_bricklet(self, ip_connection) -> BrickletOutdoorWeather:
        return self.ow_bricklet

    def get_now(self):
        return self.now


class SensorData:
    def __init__(self, temperature, humidity, last_change=0):
        self.temperature = temperature
        self.humidity = humidity
        self.last_change = last_change


class SensorServiceShould(unittest.TestCase):

    def test_getMeasures(self):
        testhost = 'testhost'
        testport = 1234
        outdoor_weather_uid = 'ow_uid'
        ip_connection = mock(IPConnection)
        when(ip_connection).connect(testhost, testport)
        when(ip_connection).disconnect()
        ow_bricklet = mock(BrickletOutdoorWeather)
        when(ow_bricklet).get_sensor_identifiers().thenReturn([7, 19])
        when(ow_bricklet).get_sensor_data(7).thenReturn(SensorData(237, 65))
        when(ow_bricklet).get_sensor_data(19).thenReturn(SensorData(65, 87))
        service = TestSensorService(outdoor_weather_uid, testhost, testport, ip_connection, ow_bricklet)

        measures = service.get_measures()

        self.assertEquals(2, len(measures))
        self.assertEqual(23.7, measures[0].temperature)
        self.assertEqual(65, measures[0].humidity)
        self.assertEqual(6.5, measures[1].temperature)
        self.assertEqual(87, measures[1].humidity)

    def test_getMeasuresNotOlderThan20Minutes(self):
        testhost = 'testhost'
        testport = 1234
        outdoor_weather_uid = 'ow_uid'
        ip_connection = mock(IPConnection)
        when(ip_connection).connect(testhost, testport)
        when(ip_connection).disconnect()
        ow_bricklet = mock(BrickletOutdoorWeather)
        when(ow_bricklet).get_sensor_identifiers().thenReturn([7, 23])
        when(ow_bricklet).get_sensor_data(7).thenReturn(SensorData(237, 65, 1200))
        when(ow_bricklet).get_sensor_data(23).thenReturn(SensorData(110, 43, 1199))
        service = TestSensorService(outdoor_weather_uid, testhost, testport, ip_connection, ow_bricklet,
                                    datetime(2022, 1, 6, 14, 23, 0))

        measures = service.get_measures()

        self.assertEquals(1, len(measures))
        self.assertEqual(11.0, measures[0].temperature)
        self.assertEqual(43, measures[0].humidity)
        self.assertEqual(datetime(2022, 1, 6, 14, 3, 1), measures[0].measured_at)


if __name__ == '__main__':
    unittest.main()
