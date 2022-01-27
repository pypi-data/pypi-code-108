from configparser import ConfigParser
import pytest
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.system.thermal.ambient.location_temperature import LocationAmbientTemperature

config = None
general_config: GeneralSimulationConfig = GeneralSimulationConfig(config)
profile_config: ProfileConfig = ProfileConfig(config)

# Ensure if path from simulation.defaults.ini to ambient temperature model works
ambient_temperature_model_config: ConfigParser = ConfigParser()
ambient_temperature_model_config.add_section('STORAGE_SYSTEM')
ambient_temperature_model_config.set('STORAGE_SYSTEM', 'AMBIENT_TEMPERATURE_MODEL', 'LocationAmbientTemperature')
storage_system_config = StorageSystemConfig(ambient_temperature_model_config)
ambient_temperature_model = str(storage_system_config.ambient_temperature_model[StorageSystemConfig.AMBIENT_TEMPERATURE_TYPE])

start_time = 0
end_time = 100
sample_time = 1
time_step_range = range(start_time, end_time, sample_time)


@pytest.fixture(scope="function")
def uut() -> LocationAmbientTemperature:
    if ambient_temperature_model == LocationAmbientTemperature.__name__:
        return LocationAmbientTemperature(profile_config, general_config)
    else:
        raise Exception('Test failed: Check link between simulation config and factory.')


@pytest.mark.parametrize("time_step", time_step_range)
def test_get_temperature(time_step: float, uut: LocationAmbientTemperature):
    assert 329.85 > uut.get_temperature(time_step) > 190.35  # K,
    # not hotter/colder than the coldest temperature recorded on earth


def test_get_initial_temperature(uut: LocationAmbientTemperature):
    assert 329.85 > uut.get_initial_temperature() > 190.35  # K,
    # not hotter/colder than the coldest temperature recorded on earth
