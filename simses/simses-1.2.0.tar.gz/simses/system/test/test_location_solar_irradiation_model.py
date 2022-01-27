import os
from configparser import ConfigParser
from datetime import datetime, timezone
import pytest
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.utils.utilities import remove_file
from simses.system.housing.abstract_housing import Housing
from simses.system.housing.forty_ft_container import FortyFtContainer
from simses.system.housing.twenty_ft_container import TwentyFtContainer
from simses.system.thermal.solar_irradiation.location import \
    LocationSolarIrradiationModel

DELIMITER: str = ','
HEADER: str = '# Unit: W/m^2\n # Latitude: 54\n # Longitude: 15'
START: int = 0
END: int = 60
STEP: int = 1


def create_file(value) -> str:
    filename: str = os.path.join(os.path.dirname(__file__), 'mockup_ghi_profile.csv')  # ghi - global horizontal irradiance
    with open(filename, mode='w') as file:
        file.write(HEADER + '\n')
        # add bad inputs
        file.write('0;0')
        file.write('\n')
        file.write('#\n')
        file.write('"""\n')
        file.write('"\n')
        file.write('   #\n')
        # add good inputs
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
    return filename


def create_general_config() -> GeneralSimulationConfig:
    conf: ConfigParser = ConfigParser()
    conf.add_section(GeneralSimulationConfig.SECTION)
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.START, date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.END, date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.TIME_STEP, str(STEP))
    return GeneralSimulationConfig(conf)


def create_data_config(filename: str) -> ProfileConfig:
    conf: ConfigParser = ConfigParser()
    conf.add_section(ProfileConfig.SECTION)
    conf.set(ProfileConfig.SECTION, ProfileConfig.THERMAL_PROFILE_DIR, os.path.dirname(filename))
    conf.set(ProfileConfig.SECTION, ProfileConfig.GLOBAL_HORIZONTAL_IRRADIATION_PROFILE, os.path.basename(filename))
    return ProfileConfig(conf)


@pytest.fixture(scope='function')
def uut(global_horizontal_irradiance, housing):
    filename = create_file(global_horizontal_irradiance)
    if housing == TwentyFtContainer.__name__:
        housing_model: Housing = TwentyFtContainer(None)
    elif housing == FortyFtContainer.__name__:
        housing_model: Housing = FortyFtContainer(None)
    uut = LocationSolarIrradiationModel(create_data_config(filename), create_general_config(), housing_model)
    yield uut
    uut.close()
    remove_file(filename)


@pytest.mark.parametrize('global_horizontal_irradiance, time_factor, housing, result',
                         [
                             (100, 1, TwentyFtContainer.__name__, 100),
                             (200, 1, TwentyFtContainer.__name__, 200),
                             (300, 1, FortyFtContainer.__name__, 300),
                             (400, 1, FortyFtContainer.__name__, 400),
                             (500, 2, FortyFtContainer.__name__, 500),
                             (600, 5, TwentyFtContainer.__name__, 600),
                             (0, 5, TwentyFtContainer.__name__, 0),
                             (10, 4, TwentyFtContainer.__name__, 10),
                             (20, 10, TwentyFtContainer.__name__, 20)
                         ]
                         )
def test_methods(time_factor, housing, result, uut):
    tstmp = START
    if housing == TwentyFtContainer.__name__:
        housing_model: Housing = TwentyFtContainer(None)
    elif housing == FortyFtContainer.__name__:
        housing_model: Housing = FortyFtContainer(None)
    while tstmp < END:
        assert uut.get_heat_load(tstmp) <= 1300 * housing_model.outer_layer.surface_area_total * housing_model.outer_layer.absorptivity
        assert abs(uut.get_global_horizontal_irradiance(tstmp) - result) <= 1e-10
        tstmp += STEP * time_factor




