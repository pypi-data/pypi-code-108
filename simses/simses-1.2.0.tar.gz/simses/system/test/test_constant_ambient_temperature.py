from configparser import ConfigParser
import pytest
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.system.thermal.ambient.constant_temperature import ConstantAmbientTemperature

constant_ambient_temperature_local_value = 25  # in C

# Ensure if path from simulation.defaults.ini to ambient temperature model works
ambient_temperature_model_config: ConfigParser = ConfigParser()
ambient_temperature_model_config.add_section('STORAGE_SYSTEM')
ambient_temperature_model_config.set('STORAGE_SYSTEM', 'AMBIENT_TEMPERATURE_MODEL', 'ConstantAmbientTemperature,35')
storage_system_config = StorageSystemConfig(ambient_temperature_model_config)
constant_ambient_temperature_config_value = float(storage_system_config.ambient_temperature_model[StorageSystemConfig.AMBIENT_TEMPERATURE_CONSTANT])

start_time = 0
end_time = 10
sample_time = 1
time_step_range = range(start_time, end_time, sample_time)

constant_temperature_values = [constant_ambient_temperature_local_value, constant_ambient_temperature_config_value]


@pytest.mark.parametrize("time_step", time_step_range)
def test_get_temperature(time_step):
    for value in constant_temperature_values:
        uut = ConstantAmbientTemperature(value)
        assert uut.get_temperature(time_step) == value + 273.15
        assert uut.get_initial_temperature() == value + 273.15
