import datetime


class Measure:
    def __init__(self, sensor_id: int, measured_at: datetime, temperature: float, humidity: float):
        self.sensor_id = sensor_id
        self.measured_at = measured_at
        self.temperature = temperature
        self.humidity = humidity

