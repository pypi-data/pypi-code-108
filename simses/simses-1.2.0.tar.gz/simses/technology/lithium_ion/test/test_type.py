from configparser import ConfigParser

import numpy as np
import pytest

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.commons.utils.utilities import all_non_abstract_subclasses_of
from simses.technology.lithium_ion.cell.NREL_dummy_cell import NRELDummyCell
from simses.technology.lithium_ion.cell.NREL_dummy_cell_2 import NRELDummyCell2
from simses.technology.lithium_ion.cell.generic import GenericCell
from simses.technology.lithium_ion.cell.isea import IseaCellType
from simses.technology.lithium_ion.cell.lfp_sony import SonyLFP
from simses.technology.lithium_ion.cell.lmo_daimler import DaimlerLMO
from simses.technology.lithium_ion.cell.lto_lmo import LTOLMO
from simses.technology.lithium_ion.cell.lto_nmc import LTONMC
from simses.technology.lithium_ion.cell.nca_panasonic_ncr import PanasonicNCA
from simses.technology.lithium_ion.cell.nmc_molicel import MolicelNMC
from simses.technology.lithium_ion.cell.nmc_samsung78Ah import Samsung78AhNMC
from simses.technology.lithium_ion.cell.nmc_samsung94Ah import Samsung94AhNMC
from simses.technology.lithium_ion.cell.nmc_samsung94Ah_hybrid import Samsung94AhNMCHybrid
from simses.technology.lithium_ion.cell.nmc_sanyo_ur18650e import SanyoNMC
from simses.technology.lithium_ion.cell.type import CellType


class TestCellType:
    # Single cell tests
    lithium_ion_state: LithiumIonState = LithiumIonState(0,0)
    step = 10
    test_values_soc = np.arange(0, 1.01, 1 / step)

    def make_lithium_ion_cell(self, lithium_ion_subclass):
        voltage = 0.1
        capacity = 0.1
        soh = 1.0
        config: ConfigParser = ConfigParser()
        if lithium_ion_subclass.__name__ in [GenericCell.__name__, NRELDummyCell.__name__, Samsung78AhNMC.__name__,
                                             NRELDummyCell2.__name__]:
            return lithium_ion_subclass(voltage, capacity, soh, BatteryConfig(config=config))
        return lithium_ion_subclass(voltage, capacity, soh, BatteryConfig(config=config), BatteryDataConfig())

    @pytest.fixture(scope="module") # module: gets only one instance
    def lithium_ion_subclass_list(self):
        return all_non_abstract_subclasses_of(CellType)

    @pytest.mark.parametrize("soc", test_values_soc)
    def test_ocv(self, soc, lithium_ion_subclass_list):
        for lithium_ion_subclass in lithium_ion_subclass_list:
            if lithium_ion_subclass.__name__ == IseaCellType.__name__:
                continue
            uut = self.make_lithium_ion_cell(lithium_ion_subclass)
            self.lithium_ion_state.soc = soc
            # all ocv values must be between the cell minimal voltage and maximum voltage
            assert uut.get_open_circuit_voltage(self.lithium_ion_state) >= uut.get_min_voltage()
            assert uut.get_open_circuit_voltage(self.lithium_ion_state) <= uut.get_max_voltage()
