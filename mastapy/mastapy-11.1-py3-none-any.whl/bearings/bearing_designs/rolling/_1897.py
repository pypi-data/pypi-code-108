'''_1897.py

CylindricalRollerBearing
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.bearings.bearing_results import _1697
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.bearings.bearing_designs.rolling import _1908
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'CylindricalRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalRollerBearing',)


class CylindricalRollerBearing(_1908.NonBarrelRollerBearing):
    '''CylindricalRollerBearing

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def reference_rotation_speed(self) -> 'float':
        '''float: 'ReferenceRotationSpeed' is the original name of this property.'''

        return self.wrapped.ReferenceRotationSpeed

    @reference_rotation_speed.setter
    def reference_rotation_speed(self, value: 'float'):
        self.wrapped.ReferenceRotationSpeed = float(value) if value else 0.0

    @property
    def permissible_axial_load_default_calculation_method(self) -> '_1697.CylindricalRollerMaxAxialLoadMethod':
        '''CylindricalRollerMaxAxialLoadMethod: 'PermissibleAxialLoadDefaultCalculationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.PermissibleAxialLoadDefaultCalculationMethod)
        return constructor.new(_1697.CylindricalRollerMaxAxialLoadMethod)(value) if value is not None else None

    @permissible_axial_load_default_calculation_method.setter
    def permissible_axial_load_default_calculation_method(self, value: '_1697.CylindricalRollerMaxAxialLoadMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.PermissibleAxialLoadDefaultCalculationMethod = value

    @property
    def capacity_lubrication_factor_for_permissible_axial_load_oil(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CapacityLubricationFactorForPermissibleAxialLoadOil' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadOil) if self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadOil is not None else None

    @capacity_lubrication_factor_for_permissible_axial_load_oil.setter
    def capacity_lubrication_factor_for_permissible_axial_load_oil(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadOil = value

    @property
    def radial_load_lubrication_factor_for_permissible_axial_load_oil(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadialLoadLubricationFactorForPermissibleAxialLoadOil' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadOil) if self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadOil is not None else None

    @radial_load_lubrication_factor_for_permissible_axial_load_oil.setter
    def radial_load_lubrication_factor_for_permissible_axial_load_oil(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadOil = value

    @property
    def capacity_lubrication_factor_for_permissible_axial_load_grease(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CapacityLubricationFactorForPermissibleAxialLoadGrease' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadGrease) if self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadGrease is not None else None

    @capacity_lubrication_factor_for_permissible_axial_load_grease.setter
    def capacity_lubrication_factor_for_permissible_axial_load_grease(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadGrease = value

    @property
    def radial_load_lubrication_factor_for_permissible_axial_load_grease(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadialLoadLubricationFactorForPermissibleAxialLoadGrease' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadGrease) if self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadGrease is not None else None

    @radial_load_lubrication_factor_for_permissible_axial_load_grease.setter
    def radial_load_lubrication_factor_for_permissible_axial_load_grease(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadGrease = value

    @property
    def diameter_scaling_factor_for_permissible_axial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterScalingFactorForPermissibleAxialLoad' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterScalingFactorForPermissibleAxialLoad) if self.wrapped.DiameterScalingFactorForPermissibleAxialLoad is not None else None

    @diameter_scaling_factor_for_permissible_axial_load.setter
    def diameter_scaling_factor_for_permissible_axial_load(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DiameterScalingFactorForPermissibleAxialLoad = value

    @property
    def diameter_exponent_factor_for_permissible_axial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterExponentFactorForPermissibleAxialLoad' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterExponentFactorForPermissibleAxialLoad) if self.wrapped.DiameterExponentFactorForPermissibleAxialLoad is not None else None

    @diameter_exponent_factor_for_permissible_axial_load.setter
    def diameter_exponent_factor_for_permissible_axial_load(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DiameterExponentFactorForPermissibleAxialLoad = value

    @property
    def allowable_axial_load_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AllowableAxialLoadFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AllowableAxialLoadFactor) if self.wrapped.AllowableAxialLoadFactor is not None else None

    @allowable_axial_load_factor.setter
    def allowable_axial_load_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AllowableAxialLoadFactor = value

    @property
    def permissible_axial_load_dimension_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleAxialLoadDimensionFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleAxialLoadDimensionFactor) if self.wrapped.PermissibleAxialLoadDimensionFactor is not None else None

    @permissible_axial_load_dimension_factor.setter
    def permissible_axial_load_dimension_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PermissibleAxialLoadDimensionFactor = value

    @property
    def permissible_axial_load_internal_dimension_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleAxialLoadInternalDimensionFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleAxialLoadInternalDimensionFactor) if self.wrapped.PermissibleAxialLoadInternalDimensionFactor is not None else None

    @permissible_axial_load_internal_dimension_factor.setter
    def permissible_axial_load_internal_dimension_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PermissibleAxialLoadInternalDimensionFactor = value
