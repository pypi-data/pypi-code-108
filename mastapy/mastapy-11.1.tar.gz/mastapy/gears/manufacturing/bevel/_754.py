'''_754.py

ConicalWheelManufacturingConfig
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import
from mastapy.gears.manufacturing.bevel.cutters import _776, _775
from mastapy.gears.manufacturing.bevel.basic_machine_settings import (
    _784, _781, _782, _783
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.bevel import _736

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CONICAL_WHEEL_MANUFACTURING_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalWheelManufacturingConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalWheelManufacturingConfig',)


class ConicalWheelManufacturingConfig(_736.ConicalGearManufacturingConfig):
    '''ConicalWheelManufacturingConfig

    This is a mastapy class.
    '''

    TYPE = _CONICAL_WHEEL_MANUFACTURING_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalWheelManufacturingConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_cutter_tilt(self) -> 'bool':
        '''bool: 'UseCutterTilt' is the original name of this property.'''

        return self.wrapped.UseCutterTilt

    @use_cutter_tilt.setter
    def use_cutter_tilt(self, value: 'bool'):
        self.wrapped.UseCutterTilt = bool(value) if value else False

    @property
    def wheel_finish_manufacturing_machine(self) -> 'str':
        '''str: 'WheelFinishManufacturingMachine' is the original name of this property.'''

        return self.wrapped.WheelFinishManufacturingMachine.SelectedItemName

    @wheel_finish_manufacturing_machine.setter
    def wheel_finish_manufacturing_machine(self, value: 'str'):
        self.wrapped.WheelFinishManufacturingMachine.SetSelectedItem(str(value) if value else '')

    @property
    def wheel_rough_manufacturing_machine(self) -> 'str':
        '''str: 'WheelRoughManufacturingMachine' is the original name of this property.'''

        return self.wrapped.WheelRoughManufacturingMachine.SelectedItemName

    @wheel_rough_manufacturing_machine.setter
    def wheel_rough_manufacturing_machine(self, value: 'str'):
        self.wrapped.WheelRoughManufacturingMachine.SetSelectedItem(str(value) if value else '')

    @property
    def wheel_rough_cutter(self) -> '_776.WheelRoughCutter':
        '''WheelRoughCutter: 'WheelRoughCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_776.WheelRoughCutter)(self.wrapped.WheelRoughCutter) if self.wrapped.WheelRoughCutter is not None else None

    @property
    def wheel_finish_cutter(self) -> '_775.WheelFinishCutter':
        '''WheelFinishCutter: 'WheelFinishCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_775.WheelFinishCutter)(self.wrapped.WheelFinishCutter) if self.wrapped.WheelFinishCutter is not None else None

    @property
    def specified_cradle_style_machine_settings(self) -> '_784.CradleStyleConicalMachineSettingsGenerated':
        '''CradleStyleConicalMachineSettingsGenerated: 'SpecifiedCradleStyleMachineSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_784.CradleStyleConicalMachineSettingsGenerated)(self.wrapped.SpecifiedCradleStyleMachineSettings) if self.wrapped.SpecifiedCradleStyleMachineSettings is not None else None

    @property
    def specified_machine_settings(self) -> '_781.BasicConicalGearMachineSettings':
        '''BasicConicalGearMachineSettings: 'SpecifiedMachineSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _781.BasicConicalGearMachineSettings.TYPE not in self.wrapped.SpecifiedMachineSettings.__class__.__mro__:
            raise CastException('Failed to cast specified_machine_settings to BasicConicalGearMachineSettings. Expected: {}.'.format(self.wrapped.SpecifiedMachineSettings.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SpecifiedMachineSettings.__class__)(self.wrapped.SpecifiedMachineSettings) if self.wrapped.SpecifiedMachineSettings is not None else None

    @property
    def specified_machine_settings_of_type_basic_conical_gear_machine_settings_formate(self) -> '_782.BasicConicalGearMachineSettingsFormate':
        '''BasicConicalGearMachineSettingsFormate: 'SpecifiedMachineSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _782.BasicConicalGearMachineSettingsFormate.TYPE not in self.wrapped.SpecifiedMachineSettings.__class__.__mro__:
            raise CastException('Failed to cast specified_machine_settings to BasicConicalGearMachineSettingsFormate. Expected: {}.'.format(self.wrapped.SpecifiedMachineSettings.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SpecifiedMachineSettings.__class__)(self.wrapped.SpecifiedMachineSettings) if self.wrapped.SpecifiedMachineSettings is not None else None

    @property
    def specified_machine_settings_of_type_basic_conical_gear_machine_settings_generated(self) -> '_783.BasicConicalGearMachineSettingsGenerated':
        '''BasicConicalGearMachineSettingsGenerated: 'SpecifiedMachineSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _783.BasicConicalGearMachineSettingsGenerated.TYPE not in self.wrapped.SpecifiedMachineSettings.__class__.__mro__:
            raise CastException('Failed to cast specified_machine_settings to BasicConicalGearMachineSettingsGenerated. Expected: {}.'.format(self.wrapped.SpecifiedMachineSettings.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SpecifiedMachineSettings.__class__)(self.wrapped.SpecifiedMachineSettings) if self.wrapped.SpecifiedMachineSettings is not None else None
