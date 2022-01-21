'''_1215.py

SplineJointDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.detailed_rigid_connectors.splines import (
    _1194, _1205, _1217, _1209,
    _1206, _1213, _1214, _1189,
    _1192, _1196, _1199, _1207,
    _1219
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.cast_exception import CastException
from mastapy.detailed_rigid_connectors import _1187
from mastapy._internal.python_net import python_net_import

_SPLINE_JOINT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'SplineJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('SplineJointDesign',)


class SplineJointDesign(_1187.DetailedRigidConnectorDesign):
    '''SplineJointDesign

    This is a mastapy class.
    '''

    TYPE = _SPLINE_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SplineJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diametral_pitch(self) -> 'float':
        '''float: 'DiametralPitch' is the original name of this property.'''

        return self.wrapped.DiametralPitch

    @diametral_pitch.setter
    def diametral_pitch(self, value: 'float'):
        self.wrapped.DiametralPitch = float(value) if value else 0.0

    @property
    def module(self) -> 'float':
        '''float: 'Module' is the original name of this property.'''

        return self.wrapped.Module

    @module.setter
    def module(self, value: 'float'):
        self.wrapped.Module = float(value) if value else 0.0

    @property
    def dudley_maximum_effective_length(self) -> 'float':
        '''float: 'DudleyMaximumEffectiveLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DudleyMaximumEffectiveLength

    @property
    def dudley_maximum_effective_length_option(self) -> 'enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption':
        '''enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption: 'DudleyMaximumEffectiveLengthOption' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DudleyMaximumEffectiveLengthOption, value) if self.wrapped.DudleyMaximumEffectiveLengthOption is not None else None

    @dudley_maximum_effective_length_option.setter
    def dudley_maximum_effective_length_option(self, value: 'enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DudleyMaximumEffectiveLengthOption = value

    @property
    def pressure_angle(self) -> 'float':
        '''float: 'PressureAngle' is the original name of this property.'''

        return self.wrapped.PressureAngle

    @pressure_angle.setter
    def pressure_angle(self, value: 'float'):
        self.wrapped.PressureAngle = float(value) if value else 0.0

    @property
    def number_of_teeth(self) -> 'int':
        '''int: 'NumberOfTeeth' is the original name of this property.'''

        return self.wrapped.NumberOfTeeth

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'int'):
        self.wrapped.NumberOfTeeth = int(value) if value else 0

    @property
    def root_type(self) -> '_1205.RootTypes':
        '''RootTypes: 'RootType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.RootType)
        return constructor.new(_1205.RootTypes)(value) if value is not None else None

    @root_type.setter
    def root_type(self, value: '_1205.RootTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.RootType = value

    @property
    def total_crowning(self) -> 'float':
        '''float: 'TotalCrowning' is the original name of this property.'''

        return self.wrapped.TotalCrowning

    @total_crowning.setter
    def total_crowning(self, value: 'float'):
        self.wrapped.TotalCrowning = float(value) if value else 0.0

    @property
    def pitch_diameter(self) -> 'float':
        '''float: 'PitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDiameter

    @property
    def circular_pitch(self) -> 'float':
        '''float: 'CircularPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CircularPitch

    @property
    def base_diameter(self) -> 'float':
        '''float: 'BaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameter

    @property
    def base_radius(self) -> 'float':
        '''float: 'BaseRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseRadius

    @property
    def number_of_teeth_in_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NumberOfTeethInContact' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NumberOfTeethInContact) if self.wrapped.NumberOfTeethInContact is not None else None

    @number_of_teeth_in_contact.setter
    def number_of_teeth_in_contact(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NumberOfTeethInContact = value

    @property
    def use_sae_stress_concentration_factor(self) -> 'bool':
        '''bool: 'UseSAEStressConcentrationFactor' is the original name of this property.'''

        return self.wrapped.UseSAEStressConcentrationFactor

    @use_sae_stress_concentration_factor.setter
    def use_sae_stress_concentration_factor(self, value: 'bool'):
        self.wrapped.UseSAEStressConcentrationFactor = bool(value) if value else False

    @property
    def user_specified_external_teeth_stress_concentration_factor(self) -> 'float':
        '''float: 'UserSpecifiedExternalTeethStressConcentrationFactor' is the original name of this property.'''

        return self.wrapped.UserSpecifiedExternalTeethStressConcentrationFactor

    @user_specified_external_teeth_stress_concentration_factor.setter
    def user_specified_external_teeth_stress_concentration_factor(self, value: 'float'):
        self.wrapped.UserSpecifiedExternalTeethStressConcentrationFactor = float(value) if value else 0.0

    @property
    def user_specified_internal_teeth_stress_concentration_factor(self) -> 'float':
        '''float: 'UserSpecifiedInternalTeethStressConcentrationFactor' is the original name of this property.'''

        return self.wrapped.UserSpecifiedInternalTeethStressConcentrationFactor

    @user_specified_internal_teeth_stress_concentration_factor.setter
    def user_specified_internal_teeth_stress_concentration_factor(self, value: 'float'):
        self.wrapped.UserSpecifiedInternalTeethStressConcentrationFactor = float(value) if value else 0.0

    @property
    def base_pitch(self) -> 'float':
        '''float: 'BasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasePitch

    @property
    def basic_space_width(self) -> 'float':
        '''float: 'BasicSpaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicSpaceWidth

    @property
    def basic_tooth_thickness(self) -> 'float':
        '''float: 'BasicToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicToothThickness

    @property
    def with_crown(self) -> 'bool':
        '''bool: 'WithCrown' is the original name of this property.'''

        return self.wrapped.WithCrown

    @with_crown.setter
    def with_crown(self, value: 'bool'):
        self.wrapped.WithCrown = bool(value) if value else False

    @property
    def before_running_in(self) -> 'bool':
        '''bool: 'BeforeRunningIn' is the original name of this property.'''

        return self.wrapped.BeforeRunningIn

    @before_running_in.setter
    def before_running_in(self, value: 'bool'):
        self.wrapped.BeforeRunningIn = bool(value) if value else False

    @property
    def spline_rating_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes: 'SplineRatingType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.SplineRatingType, value) if self.wrapped.SplineRatingType is not None else None

    @spline_rating_type.setter
    def spline_rating_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.SplineRatingType = value

    @property
    def designation(self) -> 'str':
        '''str: 'Designation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Designation

    @property
    def wall_thickness(self) -> 'float':
        '''float: 'WallThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WallThickness

    @property
    def torque_cycles(self) -> '_1209.SAETorqueCycles':
        '''SAETorqueCycles: 'TorqueCycles' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TorqueCycles)
        return constructor.new(_1209.SAETorqueCycles)(value) if value is not None else None

    @torque_cycles.setter
    def torque_cycles(self, value: '_1209.SAETorqueCycles'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TorqueCycles = value

    @property
    def fatigue_life_factor_type(self) -> '_1206.SAEFatigueLifeFactorTypes':
        '''SAEFatigueLifeFactorTypes: 'FatigueLifeFactorType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FatigueLifeFactorType)
        return constructor.new(_1206.SAEFatigueLifeFactorTypes)(value) if value is not None else None

    @fatigue_life_factor_type.setter
    def fatigue_life_factor_type(self, value: '_1206.SAEFatigueLifeFactorTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FatigueLifeFactorType = value

    @property
    def spline_fixture_type(self) -> '_1213.SplineFixtureTypes':
        '''SplineFixtureTypes: 'SplineFixtureType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SplineFixtureType)
        return constructor.new(_1213.SplineFixtureTypes)(value) if value is not None else None

    @spline_fixture_type.setter
    def spline_fixture_type(self, value: '_1213.SplineFixtureTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SplineFixtureType = value

    @property
    def use_user_input_allowable_stresses(self) -> 'bool':
        '''bool: 'UseUserInputAllowableStresses' is the original name of this property.'''

        return self.wrapped.UseUserInputAllowableStresses

    @use_user_input_allowable_stresses.setter
    def use_user_input_allowable_stresses(self, value: 'bool'):
        self.wrapped.UseUserInputAllowableStresses = bool(value) if value else False

    @property
    def minimum_effective_clearance(self) -> 'float':
        '''float: 'MinimumEffectiveClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveClearance

    @property
    def external_half(self) -> '_1214.SplineHalfDesign':
        '''SplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1214.SplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to SplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def external_half_of_type_custom_spline_half_design(self) -> '_1189.CustomSplineHalfDesign':
        '''CustomSplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1189.CustomSplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to CustomSplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def external_half_of_type_din5480_spline_half_design(self) -> '_1192.DIN5480SplineHalfDesign':
        '''DIN5480SplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1192.DIN5480SplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to DIN5480SplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def external_half_of_type_gbt3478_spline_half_design(self) -> '_1196.GBT3478SplineHalfDesign':
        '''GBT3478SplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1196.GBT3478SplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to GBT3478SplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def external_half_of_type_iso4156_spline_half_design(self) -> '_1199.ISO4156SplineHalfDesign':
        '''ISO4156SplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1199.ISO4156SplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to ISO4156SplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def external_half_of_type_sae_spline_half_design(self) -> '_1207.SAESplineHalfDesign':
        '''SAESplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1207.SAESplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to SAESplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def external_half_of_type_standard_spline_half_design(self) -> '_1219.StandardSplineHalfDesign':
        '''StandardSplineHalfDesign: 'ExternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1219.StandardSplineHalfDesign.TYPE not in self.wrapped.ExternalHalf.__class__.__mro__:
            raise CastException('Failed to cast external_half to StandardSplineHalfDesign. Expected: {}.'.format(self.wrapped.ExternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExternalHalf.__class__)(self.wrapped.ExternalHalf) if self.wrapped.ExternalHalf is not None else None

    @property
    def internal_half(self) -> '_1214.SplineHalfDesign':
        '''SplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1214.SplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to SplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None

    @property
    def internal_half_of_type_custom_spline_half_design(self) -> '_1189.CustomSplineHalfDesign':
        '''CustomSplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1189.CustomSplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to CustomSplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None

    @property
    def internal_half_of_type_din5480_spline_half_design(self) -> '_1192.DIN5480SplineHalfDesign':
        '''DIN5480SplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1192.DIN5480SplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to DIN5480SplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None

    @property
    def internal_half_of_type_gbt3478_spline_half_design(self) -> '_1196.GBT3478SplineHalfDesign':
        '''GBT3478SplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1196.GBT3478SplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to GBT3478SplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None

    @property
    def internal_half_of_type_iso4156_spline_half_design(self) -> '_1199.ISO4156SplineHalfDesign':
        '''ISO4156SplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1199.ISO4156SplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to ISO4156SplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None

    @property
    def internal_half_of_type_sae_spline_half_design(self) -> '_1207.SAESplineHalfDesign':
        '''SAESplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1207.SAESplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to SAESplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None

    @property
    def internal_half_of_type_standard_spline_half_design(self) -> '_1219.StandardSplineHalfDesign':
        '''StandardSplineHalfDesign: 'InternalHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1219.StandardSplineHalfDesign.TYPE not in self.wrapped.InternalHalf.__class__.__mro__:
            raise CastException('Failed to cast internal_half to StandardSplineHalfDesign. Expected: {}.'.format(self.wrapped.InternalHalf.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InternalHalf.__class__)(self.wrapped.InternalHalf) if self.wrapped.InternalHalf is not None else None
