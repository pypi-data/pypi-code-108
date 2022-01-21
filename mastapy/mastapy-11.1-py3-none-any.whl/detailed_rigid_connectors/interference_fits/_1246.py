'''_1246.py

InterferenceFitHalfDesign
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.detailed_rigid_connectors.interference_fits import _1247
from mastapy.bearings.tolerances import _1677, _1663, _1669
from mastapy._internal.cast_exception import CastException
from mastapy.detailed_rigid_connectors import _1188
from mastapy._internal.python_net import python_net_import

_INTERFERENCE_FIT_HALF_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.InterferenceFits', 'InterferenceFitHalfDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('InterferenceFitHalfDesign',)


class InterferenceFitHalfDesign(_1188.DetailedRigidConnectorHalfDesign):
    '''InterferenceFitHalfDesign

    This is a mastapy class.
    '''

    TYPE = _INTERFERENCE_FIT_HALF_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterferenceFitHalfDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def nominal_joint_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NominalJointDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NominalJointDiameter) if self.wrapped.NominalJointDiameter is not None else None

    @nominal_joint_diameter.setter
    def nominal_joint_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NominalJointDiameter = value

    @property
    def average_joint_diameter(self) -> 'float':
        '''float: 'AverageJointDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageJointDiameter

    @property
    def upper_deviation(self) -> 'float':
        '''float: 'UpperDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UpperDeviation

    @property
    def lower_deviation(self) -> 'float':
        '''float: 'LowerDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LowerDeviation

    @property
    def required_safety_against_plastic_strain(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RequiredSafetyAgainstPlasticStrain' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RequiredSafetyAgainstPlasticStrain) if self.wrapped.RequiredSafetyAgainstPlasticStrain is not None else None

    @required_safety_against_plastic_strain.setter
    def required_safety_against_plastic_strain(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RequiredSafetyAgainstPlasticStrain = value

    @property
    def average_surface_roughness(self) -> 'float':
        '''float: 'AverageSurfaceRoughness' is the original name of this property.'''

        return self.wrapped.AverageSurfaceRoughness

    @average_surface_roughness.setter
    def average_surface_roughness(self, value: 'float'):
        self.wrapped.AverageSurfaceRoughness = float(value) if value else 0.0

    @property
    def diameter_ratio(self) -> 'float':
        '''float: 'DiameterRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DiameterRatio

    @property
    def permissible_joint_pressure_for_fully_elastic_part(self) -> 'float':
        '''float: 'PermissibleJointPressureForFullyElasticPart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleJointPressureForFullyElasticPart

    @property
    def permissible_relative_interference_for_fully_elastic_part(self) -> 'float':
        '''float: 'PermissibleRelativeInterferenceForFullyElasticPart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleRelativeInterferenceForFullyElasticPart

    @property
    def joint_pressure_for_fully_plastic_part(self) -> 'float':
        '''float: 'JointPressureForFullyPlasticPart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.JointPressureForFullyPlasticPart

    @property
    def designation(self) -> 'str':
        '''str: 'Designation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Designation

    @property
    def stress_region(self) -> '_1247.StressRegions':
        '''StressRegions: 'StressRegion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.StressRegion)
        return constructor.new(_1247.StressRegions)(value) if value is not None else None

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def tolerance(self) -> '_1677.SupportTolerance':
        '''SupportTolerance: 'Tolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1677.SupportTolerance.TYPE not in self.wrapped.Tolerance.__class__.__mro__:
            raise CastException('Failed to cast tolerance to SupportTolerance. Expected: {}.'.format(self.wrapped.Tolerance.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Tolerance.__class__)(self.wrapped.Tolerance) if self.wrapped.Tolerance is not None else None

    @property
    def tolerance_of_type_inner_support_tolerance(self) -> '_1663.InnerSupportTolerance':
        '''InnerSupportTolerance: 'Tolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1663.InnerSupportTolerance.TYPE not in self.wrapped.Tolerance.__class__.__mro__:
            raise CastException('Failed to cast tolerance to InnerSupportTolerance. Expected: {}.'.format(self.wrapped.Tolerance.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Tolerance.__class__)(self.wrapped.Tolerance) if self.wrapped.Tolerance is not None else None

    @property
    def tolerance_of_type_outer_support_tolerance(self) -> '_1669.OuterSupportTolerance':
        '''OuterSupportTolerance: 'Tolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1669.OuterSupportTolerance.TYPE not in self.wrapped.Tolerance.__class__.__mro__:
            raise CastException('Failed to cast tolerance to OuterSupportTolerance. Expected: {}.'.format(self.wrapped.Tolerance.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Tolerance.__class__)(self.wrapped.Tolerance) if self.wrapped.Tolerance is not None else None
