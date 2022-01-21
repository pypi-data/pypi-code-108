'''_783.py

BasicConicalGearMachineSettingsGenerated
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.bevel.basic_machine_settings import _781
from mastapy._internal.python_net import python_net_import

_BASIC_CONICAL_GEAR_MACHINE_SETTINGS_GENERATED = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel.BasicMachineSettings', 'BasicConicalGearMachineSettingsGenerated')


__docformat__ = 'restructuredtext en'
__all__ = ('BasicConicalGearMachineSettingsGenerated',)


class BasicConicalGearMachineSettingsGenerated(_781.BasicConicalGearMachineSettings):
    '''BasicConicalGearMachineSettingsGenerated

    This is a mastapy class.
    '''

    TYPE = _BASIC_CONICAL_GEAR_MACHINE_SETTINGS_GENERATED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BasicConicalGearMachineSettingsGenerated.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def ratio_of_roll(self) -> 'float':
        '''float: 'RatioOfRoll' is the original name of this property.'''

        return self.wrapped.RatioOfRoll

    @ratio_of_roll.setter
    def ratio_of_roll(self, value: 'float'):
        self.wrapped.RatioOfRoll = float(value) if value else 0.0

    @property
    def basic_cradle_angle(self) -> 'float':
        '''float: 'BasicCradleAngle' is the original name of this property.'''

        return self.wrapped.BasicCradleAngle

    @basic_cradle_angle.setter
    def basic_cradle_angle(self, value: 'float'):
        self.wrapped.BasicCradleAngle = float(value) if value else 0.0

    @property
    def radial_setting(self) -> 'float':
        '''float: 'RadialSetting' is the original name of this property.'''

        return self.wrapped.RadialSetting

    @radial_setting.setter
    def radial_setting(self, value: 'float'):
        self.wrapped.RadialSetting = float(value) if value else 0.0

    @property
    def blank_offset(self) -> 'float':
        '''float: 'BlankOffset' is the original name of this property.'''

        return self.wrapped.BlankOffset

    @blank_offset.setter
    def blank_offset(self, value: 'float'):
        self.wrapped.BlankOffset = float(value) if value else 0.0

    @property
    def modified_roll_coefficient_c(self) -> 'float':
        '''float: 'ModifiedRollCoefficientC' is the original name of this property.'''

        return self.wrapped.ModifiedRollCoefficientC

    @modified_roll_coefficient_c.setter
    def modified_roll_coefficient_c(self, value: 'float'):
        self.wrapped.ModifiedRollCoefficientC = float(value) if value else 0.0

    @property
    def modified_roll_coefficient_d(self) -> 'float':
        '''float: 'ModifiedRollCoefficientD' is the original name of this property.'''

        return self.wrapped.ModifiedRollCoefficientD

    @modified_roll_coefficient_d.setter
    def modified_roll_coefficient_d(self, value: 'float'):
        self.wrapped.ModifiedRollCoefficientD = float(value) if value else 0.0
