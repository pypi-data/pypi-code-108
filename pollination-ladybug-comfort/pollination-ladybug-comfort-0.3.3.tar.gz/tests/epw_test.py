from pollination.ladybug_comfort.epw import PrevailingTemperature, AirSpeedJson
from queenbee.plugin.function import Function


def test_prevailing_temperature():
    function = PrevailingTemperature().queenbee
    assert function.name == 'prevailing-temperature'
    assert isinstance(function, Function)


def test_air_speed_json():
    function = AirSpeedJson().queenbee
    assert function.name == 'air-speed-json'
    assert isinstance(function, Function)
