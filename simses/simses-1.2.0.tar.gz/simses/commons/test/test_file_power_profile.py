import os
from configparser import ConfigParser
from datetime import datetime, timezone
import pytest
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.power.file import FilePowerProfile
from simses.commons.utils.utilities import remove_file

DELIMITER: str = ','
HEADER: str = '# Unit: W'
START: int = 0
END: int = 60
STEP: int = 1


def create_file(value):
    filename: str = os.path.join(os.path.dirname(__file__), 'mockup_power_profile.csv')
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


def create_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('GENERAL')
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set('GENERAL', 'START', date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set('GENERAL', 'END', date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set('GENERAL', 'TIME_STEP', str(STEP))
    return GeneralSimulationConfig(config=conf)


@pytest.fixture(scope='function')
def uut(power, scaling_factor):
    filename = create_file(power)
    uut = FilePowerProfile(config=create_config(), filename=filename, delimiter=DELIMITER, scaling_factor=scaling_factor)
    yield uut
    uut.close()
    remove_file(filename)


@pytest.mark.parametrize('power, time_factor, scaling_factor, result',
                         [
                            (0, 1, 0, 0),
                            (0, 1, 2, 0),
                            (1, 1, 1, 1),
                            (2, 1, 3, 6),
                            (6, 0.5, 0.5, 3),
                            (1, 5, 1, 1),
                            (0, 1, 1, 0)
                         ]
                         )
def test_next(time_factor, result, uut):
    tstmp = START
    while tstmp < END:
        assert abs(uut.next(tstmp) - result) <= 1e-10
        tstmp += STEP * time_factor
