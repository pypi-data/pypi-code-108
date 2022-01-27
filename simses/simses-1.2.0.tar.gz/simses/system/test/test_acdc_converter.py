import numpy as np
import pytest

from simses.commons.config.data.power_electronics import PowerElectronicsConfig
from simses.commons.utils.utilities import all_non_abstract_subclasses_of
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter
from simses.system.power_electronics.acdc_converter.bonfiglioli import BonfiglioliAcDcConverter
from simses.system.power_electronics.acdc_converter.fix_efficiency import FixEfficiencyAcDcConverter
from simses.system.power_electronics.acdc_converter.no_loss import NoLossAcDcConverter
from simses.system.power_electronics.acdc_converter.notton import NottonAcDcConverter
from simses.system.power_electronics.acdc_converter.notton_loss import NottonLossAcDcConverter
from simses.system.power_electronics.acdc_converter.sinamics import Sinamics120AcDcConverter
from simses.system.power_electronics.acdc_converter.stable import M2bAcDcConverter
from simses.system.power_electronics.acdc_converter.stacked import AcDcConverterIdenticalStacked
from simses.system.power_electronics.acdc_converter.sungrow import SungrowAcDcConverter


class TestClassAcDc:

    max_power = 40000
    step = 10
    test_values = list(range(0, max_power, int(max_power / step)))
    abs_voltage = 20

    def make_converter(self, converter_subclass, max_power) -> AcDcConverter:
        if converter_subclass in [Sinamics120AcDcConverter]:
            return converter_subclass(max_power, PowerElectronicsConfig())
        elif converter_subclass in [AcDcConverterIdenticalStacked]:
            return AcDcConverterIdenticalStacked(3, 0.8, NottonAcDcConverter(max_power))
        elif converter_subclass in [BonfiglioliAcDcConverter, FixEfficiencyAcDcConverter,
                                    NoLossAcDcConverter, NottonAcDcConverter, NottonLossAcDcConverter, M2bAcDcConverter,
                                    SungrowAcDcConverter]:
            return converter_subclass(max_power)
        else:
            raise Exception('AcDcConverter is not tested')

    @pytest.fixture(scope="function")#module: gets only one instance
    def converter_subclass_list(self):
        return all_non_abstract_subclasses_of(AcDcConverter, [AcDcConverterIdenticalStacked])

    @pytest.mark.parametrize("ac_power", test_values)#sadly no function objects can be passed
    def test_sign_to_ac(self, ac_power, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
            assert uut.to_ac(ac_power, self.abs_voltage) == 0  # "charge"
            assert uut.to_ac(-ac_power, self.abs_voltage) <= -ac_power  # discharge

    @pytest.mark.parametrize("ac_power", test_values)
    def test_sign_to_dc(self, ac_power, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
            assert uut.to_dc(ac_power, self.abs_voltage) <= ac_power  # charge
            assert uut.to_dc(-ac_power, self.abs_voltage) == 0  # "discharge"

    @pytest.mark.parametrize("dc_power", test_values)
    def test_sign_to_ac_reverse(self, dc_power, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
            assert uut.to_ac_reverse(dc_power, self.abs_voltage) == 0  # "charge"
            assert uut.to_ac_reverse(-dc_power, self.abs_voltage) >= -dc_power  # discharge

    @pytest.mark.parametrize("dc_power", test_values)
    def test_sign_to_dc_reverse(self, dc_power, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
            assert uut.to_dc_reverse(dc_power, self.abs_voltage) >= dc_power  # charge
            assert uut.to_dc_reverse(-dc_power, self.abs_voltage) == 0  # "discharge"

    def test_max_power_to_ac(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                assert uut.to_ac(self.max_power * 2, self.abs_voltage) <= self.max_power
                assert uut.to_ac(-self.max_power * 2, self.abs_voltage) >= self.max_power

    def test_max_power_to_dc(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                assert uut.to_dc(self.max_power * 2, self.abs_voltage) <= self.max_power
                assert uut.to_dc(-self.max_power * 2, self.abs_voltage) >= self.max_power

    def test_max_power_to_ac_reverse(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                assert uut.to_ac_reverse(self.max_power * 2, self.abs_voltage) <= self.max_power
                assert uut.to_ac_reverse(-self.max_power * 2, self.abs_voltage) >= self.max_power

    def test_max_power_to_dc_reverse(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                assert uut.to_dc_reverse(self.max_power * 2, self.abs_voltage) <= self.max_power
                assert uut.to_dc_reverse(-self.max_power * 2, self.abs_voltage) >= self.max_power

    def test_to_ac_is_nan(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                print(converter_subclass, np.isnan(uut.to_ac(np.nan, self.abs_voltage)))
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                uut.to_ac(np.nan, self.abs_voltage)

    def test_to_dc_is_nan(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                uut.to_dc(np.nan, self.abs_voltage)

    def test_to_ac_reverse_is_nan(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                uut.to_ac_reverse(np.nan, self.abs_voltage)

    def test_to_dc_reverse_is_nan(self, converter_subclass_list):
        for converter_subclass in converter_subclass_list:
            with pytest.raises(Exception):
                uut: AcDcConverter = self.make_converter(converter_subclass, self.max_power)
                uut.to_dc_reverse(np.nan, self.abs_voltage)
