from configparser import ConfigParser
from datetime import datetime

import pytest
from pytz import timezone

from simses.commons.data.no_data_handler import NoDataHandler
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.battery import LithiumIonBattery
from simses.technology.lithium_ion.cell.generic import GenericCell
from simses.technology.lithium_ion.cell.lfp_sony import SonyLFP

THRESHOLD: float = 1e-1

voltage: float = 600  # V
capacity: float = 60e3  # Wh
soh: float = 1.0  # p.u.

start_soc: float = 0.5  # p.u.
start_temperature: float = 300  # K

max_current: float = 205  # A (for Generic Cell in current setup)

time_step: float = 60  # s

start_date: str = '2014-01-01 00:00:00'
date: datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
start_time: float = timezone('UTC').localize(date).timestamp()

battery_config: ConfigParser = ConfigParser()
battery_config.add_section('GENERAL')
battery_config.set('GENERAL', 'START', start_date)
battery_config.set('GENERAL', 'END', '2014-01-02 00:00:00')
battery_config.set('GENERAL', 'TIME_STEP', str(time_step))
battery_config.add_section('BATTERY')
battery_config.set('BATTERY', 'START_SOC', str(start_soc))
battery_config.set('BATTERY', 'MIN_SOC', str(0.0))
battery_config.set('BATTERY', 'MAX_SOC', str(1.0))
battery_config.set('BATTERY', 'EOL', str(0.6))
battery_config.set('BATTERY', 'START_SOH', str(soh))


@pytest.fixture()
def uut(cell: str) -> LithiumIonBattery:
    return LithiumIonBattery(cell=cell, voltage=voltage, capacity=capacity, soc=start_soc, soh=soh,
                             data_export=NoDataHandler(), temperature=start_temperature, storage_id=1, system_id=1,
                             config=battery_config)


@pytest.mark.parametrize('cell, current, result',
                         [
                            (SonyLFP.__name__, 10, 10),
                            (GenericCell.__name__, 10, 10),
                            (GenericCell.__name__, 10, 10)
                         ]
                         )
def test_current(uut: LithiumIonBattery, current: float, result: float):
    uut.distribute_and_run(start_time + time_step, current, voltage)
    battery_state: LithiumIonState = uut.state
    assert abs(battery_state.current - result) <= THRESHOLD
