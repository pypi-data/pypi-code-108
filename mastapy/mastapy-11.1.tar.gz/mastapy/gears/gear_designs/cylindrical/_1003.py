'''_1003.py

GearManufacturingConfigSetupViewModel
'''


from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.gears.manufacturing.cylindrical import _583, _584
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_MANUFACTURING_CONFIG_SETUP_VIEW_MODEL = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'GearManufacturingConfigSetupViewModel')


__docformat__ = 'restructuredtext en'
__all__ = ('GearManufacturingConfigSetupViewModel',)


class GearManufacturingConfigSetupViewModel(_0.APIBase):
    '''GearManufacturingConfigSetupViewModel

    This is a mastapy class.
    '''

    TYPE = _GEAR_MANUFACTURING_CONFIG_SETUP_VIEW_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearManufacturingConfigSetupViewModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def finishing_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods: 'FinishingMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.FinishingMethod, value) if self.wrapped.FinishingMethod is not None else None

    @finishing_method.setter
    def finishing_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftFinishingMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.FinishingMethod = value

    @property
    def roughing_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods':
        '''enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods: 'RoughingMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.RoughingMethod, value) if self.wrapped.RoughingMethod is not None else None

    @roughing_method.setter
    def roughing_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CylindricalMftRoughingMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.RoughingMethod = value

    @property
    def rough_pressure_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RoughPressureAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RoughPressureAngle) if self.wrapped.RoughPressureAngle is not None else None

    @rough_pressure_angle.setter
    def rough_pressure_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RoughPressureAngle = value

    @property
    def create_new_suitable_cutters(self) -> 'bool':
        '''bool: 'CreateNewSuitableCutters' is the original name of this property.'''

        return self.wrapped.CreateNewSuitableCutters

    @create_new_suitable_cutters.setter
    def create_new_suitable_cutters(self, value: 'bool'):
        self.wrapped.CreateNewSuitableCutters = bool(value) if value else False

    @property
    def use_as_design_mode_geometry(self) -> 'bool':
        '''bool: 'UseAsDesignModeGeometry' is the original name of this property.'''

        return self.wrapped.UseAsDesignModeGeometry

    @use_as_design_mode_geometry.setter
    def use_as_design_mode_geometry(self, value: 'bool'):
        self.wrapped.UseAsDesignModeGeometry = bool(value) if value else False

    @property
    def gear_name(self) -> 'str':
        '''str: 'GearName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearName
