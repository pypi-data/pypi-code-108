'''_967.py

CylindricalGearCuttingOptions
'''


from mastapy._internal.implicit import enum_with_selected_value, list_with_selected_item
from mastapy.gears.gear_designs.cylindrical import (
    _1005, _963, _965, _979,
    _1030, _987
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical import _572
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_CUTTING_OPTIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearCuttingOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearCuttingOptions',)


class CylindricalGearCuttingOptions(_0.APIBase):
    '''CylindricalGearCuttingOptions

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_CUTTING_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearCuttingOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def geometry_specification_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_GeometrySpecificationType':
        '''enum_with_selected_value.EnumWithSelectedValue_GeometrySpecificationType: 'GeometrySpecificationType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_GeometrySpecificationType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.GeometrySpecificationType, value) if self.wrapped.GeometrySpecificationType is not None else None

    @geometry_specification_type.setter
    def geometry_specification_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_GeometrySpecificationType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_GeometrySpecificationType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.GeometrySpecificationType = value

    @property
    def use_design_default_toleranced_measurement(self) -> 'bool':
        '''bool: 'UseDesignDefaultTolerancedMeasurement' is the original name of this property.'''

        return self.wrapped.UseDesignDefaultTolerancedMeasurement

    @use_design_default_toleranced_measurement.setter
    def use_design_default_toleranced_measurement(self, value: 'bool'):
        self.wrapped.UseDesignDefaultTolerancedMeasurement = bool(value) if value else False

    @property
    def thickness_for_analyses(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'ThicknessForAnalyses' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.ThicknessForAnalyses) if self.wrapped.ThicknessForAnalyses is not None else None

    @thickness_for_analyses.setter
    def thickness_for_analyses(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.ThicknessForAnalyses = value

    @property
    def cylindrical_gear_cutter(self) -> '_963.CylindricalGearAbstractRack':
        '''CylindricalGearAbstractRack: 'CylindricalGearCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _963.CylindricalGearAbstractRack.TYPE not in self.wrapped.CylindricalGearCutter.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_cutter to CylindricalGearAbstractRack. Expected: {}.'.format(self.wrapped.CylindricalGearCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearCutter.__class__)(self.wrapped.CylindricalGearCutter) if self.wrapped.CylindricalGearCutter is not None else None

    @property
    def cylindrical_gear_cutter_of_type_cylindrical_gear_basic_rack(self) -> '_965.CylindricalGearBasicRack':
        '''CylindricalGearBasicRack: 'CylindricalGearCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _965.CylindricalGearBasicRack.TYPE not in self.wrapped.CylindricalGearCutter.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_cutter to CylindricalGearBasicRack. Expected: {}.'.format(self.wrapped.CylindricalGearCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearCutter.__class__)(self.wrapped.CylindricalGearCutter) if self.wrapped.CylindricalGearCutter is not None else None

    @property
    def cylindrical_gear_cutter_of_type_cylindrical_gear_pinion_type_cutter(self) -> '_979.CylindricalGearPinionTypeCutter':
        '''CylindricalGearPinionTypeCutter: 'CylindricalGearCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _979.CylindricalGearPinionTypeCutter.TYPE not in self.wrapped.CylindricalGearCutter.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_cutter to CylindricalGearPinionTypeCutter. Expected: {}.'.format(self.wrapped.CylindricalGearCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearCutter.__class__)(self.wrapped.CylindricalGearCutter) if self.wrapped.CylindricalGearCutter is not None else None

    @property
    def cylindrical_gear_cutter_of_type_standard_rack(self) -> '_1030.StandardRack':
        '''StandardRack: 'CylindricalGearCutter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1030.StandardRack.TYPE not in self.wrapped.CylindricalGearCutter.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_cutter to StandardRack. Expected: {}.'.format(self.wrapped.CylindricalGearCutter.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearCutter.__class__)(self.wrapped.CylindricalGearCutter) if self.wrapped.CylindricalGearCutter is not None else None

    @property
    def manufacturing_configuration_selection(self) -> '_987.CylindricalGearSetManufacturingConfigurationSelection':
        '''CylindricalGearSetManufacturingConfigurationSelection: 'ManufacturingConfigurationSelection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_987.CylindricalGearSetManufacturingConfigurationSelection)(self.wrapped.ManufacturingConfigurationSelection) if self.wrapped.ManufacturingConfigurationSelection is not None else None

    @property
    def manufacturing_configuration(self) -> '_572.CylindricalGearManufacturingConfig':
        '''CylindricalGearManufacturingConfig: 'ManufacturingConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_572.CylindricalGearManufacturingConfig)(self.wrapped.ManufacturingConfiguration) if self.wrapped.ManufacturingConfiguration is not None else None
