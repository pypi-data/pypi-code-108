'''_1814.py

PermissibleContinuousAxialLoadResults
'''


from mastapy.bearings.bearing_results import _1697
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PERMISSIBLE_CONTINUOUS_AXIAL_LOAD_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'PermissibleContinuousAxialLoadResults')


__docformat__ = 'restructuredtext en'
__all__ = ('PermissibleContinuousAxialLoadResults',)


class PermissibleContinuousAxialLoadResults(_0.APIBase):
    '''PermissibleContinuousAxialLoadResults

    This is a mastapy class.
    '''

    TYPE = _PERMISSIBLE_CONTINUOUS_AXIAL_LOAD_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PermissibleContinuousAxialLoadResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def calculation_method(self) -> '_1697.CylindricalRollerMaxAxialLoadMethod':
        '''CylindricalRollerMaxAxialLoadMethod: 'CalculationMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.CalculationMethod)
        return constructor.new(_1697.CylindricalRollerMaxAxialLoadMethod)(value) if value is not None else None

    @property
    def permissible_continuous_axial_load_skf(self) -> 'float':
        '''float: 'PermissibleContinuousAxialLoadSKF' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContinuousAxialLoadSKF

    @property
    def permissible_axial_load_for_brief_periods_skf(self) -> 'float':
        '''float: 'PermissibleAxialLoadForBriefPeriodsSKF' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAxialLoadForBriefPeriodsSKF

    @property
    def permissible_axial_load_for_occasional_peak_loads_skf(self) -> 'float':
        '''float: 'PermissibleAxialLoadForOccasionalPeakLoadsSKF' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAxialLoadForOccasionalPeakLoadsSKF

    @property
    def capacity_lubrication_factor_for_permissible_axial_load_oil(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CapacityLubricationFactorForPermissibleAxialLoadOil' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadOil) if self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadOil is not None else None

    @property
    def radial_load_lubrication_factor_for_permissible_axial_load_oil(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadialLoadLubricationFactorForPermissibleAxialLoadOil' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadOil) if self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadOil is not None else None

    @property
    def capacity_lubrication_factor_for_permissible_axial_load_grease(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CapacityLubricationFactorForPermissibleAxialLoadGrease' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadGrease) if self.wrapped.CapacityLubricationFactorForPermissibleAxialLoadGrease is not None else None

    @property
    def radial_load_lubrication_factor_for_permissible_axial_load_grease(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadialLoadLubricationFactorForPermissibleAxialLoadGrease' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadGrease) if self.wrapped.RadialLoadLubricationFactorForPermissibleAxialLoadGrease is not None else None

    @property
    def diameter_scaling_factor_for_permissible_axial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterScalingFactorForPermissibleAxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterScalingFactorForPermissibleAxialLoad) if self.wrapped.DiameterScalingFactorForPermissibleAxialLoad is not None else None

    @property
    def diameter_exponent_factor_for_permissible_axial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterExponentFactorForPermissibleAxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterExponentFactorForPermissibleAxialLoad) if self.wrapped.DiameterExponentFactorForPermissibleAxialLoad is not None else None

    @property
    def permissible_axial_loading_nachi(self) -> 'float':
        '''float: 'PermissibleAxialLoadingNACHI' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAxialLoadingNACHI

    @property
    def allowable_axial_load_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AllowableAxialLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AllowableAxialLoadFactor) if self.wrapped.AllowableAxialLoadFactor is not None else None

    @property
    def permissible_axial_load_schaeffler(self) -> 'float':
        '''float: 'PermissibleAxialLoadSchaeffler' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAxialLoadSchaeffler

    @property
    def maximum_permissible_axial_load_schaeffler(self) -> 'float':
        '''float: 'MaximumPermissibleAxialLoadSchaeffler' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPermissibleAxialLoadSchaeffler

    @property
    def permissible_axial_load_under_shaft_deflection_schaeffler(self) -> 'float':
        '''float: 'PermissibleAxialLoadUnderShaftDeflectionSchaeffler' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleAxialLoadUnderShaftDeflectionSchaeffler

    @property
    def permissible_axial_load_dimension_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleAxialLoadDimensionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleAxialLoadDimensionFactor) if self.wrapped.PermissibleAxialLoadDimensionFactor is not None else None

    @property
    def allowable_constant_axial_load_ntn(self) -> 'float':
        '''float: 'AllowableConstantAxialLoadNTN' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableConstantAxialLoadNTN

    @property
    def allowable_intermittent_axial_load_ntn(self) -> 'float':
        '''float: 'AllowableIntermittentAxialLoadNTN' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableIntermittentAxialLoadNTN

    @property
    def allowable_momentary_axial_load_ntn(self) -> 'float':
        '''float: 'AllowableMomentaryAxialLoadNTN' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableMomentaryAxialLoadNTN

    @property
    def permissible_axial_load_internal_dimension_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleAxialLoadInternalDimensionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleAxialLoadInternalDimensionFactor) if self.wrapped.PermissibleAxialLoadInternalDimensionFactor is not None else None

    @property
    def axial_load(self) -> 'float':
        '''float: 'AxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialLoad

    @property
    def safety_factor(self) -> 'float':
        '''float: 'SafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactor
