'''_751.py

ConicalSetManufacturingConfig
'''


from typing import List

from mastapy._internal.implicit import enum_with_selected_value
from mastapy.gears.gear_designs.conical import _1105, _1104
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.gears.manufacturing.bevel import _736, _745, _753
from mastapy._internal.python_net import python_net_import

_CONICAL_SET_MANUFACTURING_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalSetManufacturingConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalSetManufacturingConfig',)


class ConicalSetManufacturingConfig(_753.ConicalSetMicroGeometryConfigBase):
    '''ConicalSetManufacturingConfig

    This is a mastapy class.
    '''

    TYPE = _CONICAL_SET_MANUFACTURING_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalSetManufacturingConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def manufacture_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods: 'ManufactureMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ManufactureMethod, value) if self.wrapped.ManufactureMethod is not None else None

    @manufacture_method.setter
    def manufacture_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ManufactureMethod = value

    @property
    def machine_setting_calculation_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods: 'MachineSettingCalculationMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MachineSettingCalculationMethod, value) if self.wrapped.MachineSettingCalculationMethod is not None else None

    @machine_setting_calculation_method.setter
    def machine_setting_calculation_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MachineSettingCalculationMethod = value

    @property
    def gear_manufacturing_configurations(self) -> 'List[_736.ConicalGearManufacturingConfig]':
        '''List[ConicalGearManufacturingConfig]: 'GearManufacturingConfigurations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearManufacturingConfigurations, constructor.new(_736.ConicalGearManufacturingConfig))
        return value

    @property
    def meshes(self) -> 'List[_745.ConicalMeshManufacturingConfig]':
        '''List[ConicalMeshManufacturingConfig]: 'Meshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Meshes, constructor.new(_745.ConicalMeshManufacturingConfig))
        return value
