from configparser import ConfigParser
import pytest
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.system.housing.abstract_housing import Housing
from simses.system.housing.forty_ft_container import FortyFtContainer
from simses.system.housing.twenty_ft_container import TwentyFtContainer
from simses.system.thermal.solar_irradiation.location import \
    LocationSolarIrradiationModel


class TestLocationSolarIrradiationModel:

    none_config = None
    general_config = GeneralSimulationConfig(none_config)
    profile_config = ProfileConfig(none_config)

    temperature: float = 300  # K

    # Ensure if path from simulation.defaults.ini to ambient temperature model works
    solar_irradiation_model_config: ConfigParser = ConfigParser()
    solar_irradiation_model_config.add_section('STORAGE_SYSTEM')
    solar_irradiation_model_config.set('STORAGE_SYSTEM', 'SOLAR_IRRADIATION_MODEL', 'LocationSolarIrradiationModel')
    storage_system_config = StorageSystemConfig(solar_irradiation_model_config)
    solar_irradiation_model = str(storage_system_config.solar_irradiation_model[StorageSystemConfig.SOLAR_IRRADIATION_TYPE])

    # Check compatibility of LocationSolarIrradiationModel with each Housing Model and Ambient Temperature Model
    # ambient_temperature_models = [LocationAmbientTemperature(temperature_config, general_config), ConstantAmbientTemperature()]
    housing_models = list()
    # for model in ambient_temperature_models:
    housing_models.append(TwentyFtContainer(list(), temperature))
    housing_models.append(FortyFtContainer(list(), temperature))

    start_time = 0
    end_time = 100
    sample_time = 1
    time_step_range = range(start_time, end_time, sample_time)

    def create_model(self, housing: Housing):
        if self.solar_irradiation_model == LocationSolarIrradiationModel.__name__:
            return LocationSolarIrradiationModel(self.profile_config, self.general_config, housing)
        else:
            raise Exception('Test failed: Check link between simulation config and factory.')

    @pytest.mark.parametrize("time_step", time_step_range)
    def test_get_heat_load_timestep(self, time_step):
        for housing_type in self.housing_models:
            uut: LocationSolarIrradiationModel = self.create_model(housing_type)
            assert 1400 >= uut.get_global_horizontal_irradiance(time_step) >= 0
            assert (1400 * (2 * (housing_type.outer_layer.surface_area_long_side + housing_type.outer_layer.surface_area_short_side) + housing_type.outer_layer.surface_area_roof)) > uut.get_heat_load(0)
