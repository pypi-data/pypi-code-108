from enum import Enum


class TemperatureLevel(Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'


HIGH_TEMPERATURE = 23.5
LEVEL_FROM_TEMP = {
    TemperatureLevel.LOW: lambda temp: temp < 15,
    TemperatureLevel.MEDIUM: lambda temp: 15 <= temp < HIGH_TEMPERATURE,
    TemperatureLevel.HIGH: lambda _temp: True
}


def get_level(temperature: float):
    return next((key for key in LEVEL_FROM_TEMP if LEVEL_FROM_TEMP[key](temperature)), TemperatureLevel.MEDIUM)
