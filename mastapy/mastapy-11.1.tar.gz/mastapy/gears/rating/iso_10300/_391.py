'''_391.py

ISO10300MeshSingleFlankRatingMethodB1
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import (
    _359, _345, _348, _356
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.iso_10300 import _388
from mastapy._internal.python_net import python_net_import

_ISO10300_MESH_SINGLE_FLANK_RATING_METHOD_B1 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300MeshSingleFlankRatingMethodB1')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300MeshSingleFlankRatingMethodB1',)


class ISO10300MeshSingleFlankRatingMethodB1(_388.ISO10300MeshSingleFlankRating['_356.VirtualCylindricalGearISO10300MethodB1']):
    '''ISO10300MeshSingleFlankRatingMethodB1

    This is a mastapy class.
    '''

    TYPE = _ISO10300_MESH_SINGLE_FLANK_RATING_METHOD_B1

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300MeshSingleFlankRatingMethodB1.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def transverse_load_factors_for_contact_method_b1(self) -> 'float':
        '''float: 'TransverseLoadFactorsForContactMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorsForContactMethodB1

    @property
    def transverse_load_factors_for_bending_method_b1(self) -> 'float':
        '''float: 'TransverseLoadFactorsForBendingMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorsForBendingMethodB1

    @property
    def contact_stress_method_b1(self) -> 'float':
        '''float: 'ContactStressMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressMethodB1

    @property
    def contact_stress_use_bevel_slip_factor_method_b1(self) -> 'float':
        '''float: 'ContactStressUseBevelSlipFactorMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressUseBevelSlipFactorMethodB1

    @property
    def nominal_value_of_contact_stress_method_b1(self) -> 'float':
        '''float: 'NominalValueOfContactStressMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalValueOfContactStressMethodB1

    @property
    def nominal_normal_force_of_virtual_cylindrical_gear_at_mean_point_p(self) -> 'float':
        '''float: 'NominalNormalForceOfVirtualCylindricalGearAtMeanPointP' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalNormalForceOfVirtualCylindricalGearAtMeanPointP

    @property
    def mid_zone_factor(self) -> 'float':
        '''float: 'MidZoneFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MidZoneFactor

    @property
    def area_above_the_tip_contact_line_for_contact(self) -> 'float':
        '''float: 'AreaAboveTheTipContactLineForContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaAboveTheTipContactLineForContact

    @property
    def area_above_the_middle_contact_line_for_contact(self) -> 'float':
        '''float: 'AreaAboveTheMiddleContactLineForContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaAboveTheMiddleContactLineForContact

    @property
    def area_above_the_root_contact_line_for_contact(self) -> 'float':
        '''float: 'AreaAboveTheRootContactLineForContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaAboveTheRootContactLineForContact

    @property
    def area_above_the_tip_contact_line_for_bending(self) -> 'float':
        '''float: 'AreaAboveTheTipContactLineForBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaAboveTheTipContactLineForBending

    @property
    def area_above_the_middle_contact_line_for_bending(self) -> 'float':
        '''float: 'AreaAboveTheMiddleContactLineForBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaAboveTheMiddleContactLineForBending

    @property
    def area_above_the_root_contact_line_for_bending(self) -> 'float':
        '''float: 'AreaAboveTheRootContactLineForBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaAboveTheRootContactLineForBending

    @property
    def the_ratio_of_maximum_load_over_the_middle_contact_line_and_total_load(self) -> 'float':
        '''float: 'TheRatioOfMaximumLoadOverTheMiddleContactLineAndTotalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TheRatioOfMaximumLoadOverTheMiddleContactLineAndTotalLoad

    @property
    def load_sharing_factor_pitting(self) -> 'float':
        '''float: 'LoadSharingFactorPitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingFactorPitting

    @property
    def bevel_gear_factor(self) -> 'float':
        '''float: 'BevelGearFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BevelGearFactor

    @property
    def hypoid_factor(self) -> 'float':
        '''float: 'HypoidFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HypoidFactor

    @property
    def sliding_velocity_at_mean_point_p(self) -> 'float':
        '''float: 'SlidingVelocityAtMeanPointP' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingVelocityAtMeanPointP

    @property
    def sliding_velocity_parallel_to_the_contact_line(self) -> 'float':
        '''float: 'SlidingVelocityParallelToTheContactLine' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingVelocityParallelToTheContactLine

    @property
    def sum_of_velocities_in_profile_direction(self) -> 'float':
        '''float: 'SumOfVelocitiesInProfileDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumOfVelocitiesInProfileDirection

    @property
    def sum_of_velocities_in_lengthwise_direction(self) -> 'float':
        '''float: 'SumOfVelocitiesInLengthwiseDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumOfVelocitiesInLengthwiseDirection

    @property
    def sum_of_velocities(self) -> 'float':
        '''float: 'SumOfVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumOfVelocities

    @property
    def inclination_angle_of_the_sum_of_velocities_vector(self) -> 'float':
        '''float: 'InclinationAngleOfTheSumOfVelocitiesVector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InclinationAngleOfTheSumOfVelocitiesVector

    @property
    def sum_of_velocities_vertical_to_the_contact_line(self) -> 'float':
        '''float: 'SumOfVelocitiesVerticalToTheContactLine' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumOfVelocitiesVerticalToTheContactLine

    @property
    def nominal_value_of_contact_stress_using_bevel_slip_factor_method_b1(self) -> 'float':
        '''float: 'NominalValueOfContactStressUsingBevelSlipFactorMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalValueOfContactStressUsingBevelSlipFactorMethodB1

    @property
    def pinion_bevel_slip_factor(self) -> 'float':
        '''float: 'PinionBevelSlipFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionBevelSlipFactor

    @property
    def wheel_bevel_slip_factor(self) -> 'float':
        '''float: 'WheelBevelSlipFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelBevelSlipFactor

    @property
    def size_factor(self) -> 'float':
        '''float: 'SizeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactor

    @property
    def contact_ratio_factor_for_bending_method_b1(self) -> 'float':
        '''float: 'ContactRatioFactorForBendingMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioFactorForBendingMethodB1

    @property
    def bevel_spiral_angle_factor(self) -> 'float':
        '''float: 'BevelSpiralAngleFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BevelSpiralAngleFactor

    @property
    def auxiliary_value_abs(self) -> 'float':
        '''float: 'AuxiliaryValueABS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryValueABS

    @property
    def auxiliary_value_bbs(self) -> 'float':
        '''float: 'AuxiliaryValueBBS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryValueBBS

    @property
    def auxiliary_value_cbs(self) -> 'float':
        '''float: 'AuxiliaryValueCBS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryValueCBS

    @property
    def developed_length_of_one_tooth_as_the_face_width_of_the_calculation_model(self) -> 'float':
        '''float: 'DevelopedLengthOfOneToothAsTheFaceWidthOfTheCalculationModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DevelopedLengthOfOneToothAsTheFaceWidthOfTheCalculationModel

    @property
    def part_of_the_models_face_width_covered_by_the_constance(self) -> 'float':
        '''float: 'PartOfTheModelsFaceWidthCoveredByTheConstance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PartOfTheModelsFaceWidthCoveredByTheConstance

    @property
    def average_tooth_depth(self) -> 'float':
        '''float: 'AverageToothDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageToothDepth

    @property
    def load_sharing_factor_bending(self) -> 'float':
        '''float: 'LoadSharingFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingFactorBending

    @property
    def virtual_cylindrical_gear_set_method_b1(self) -> '_359.VirtualCylindricalGearSetISO10300MethodB1':
        '''VirtualCylindricalGearSetISO10300MethodB1: 'VirtualCylindricalGearSetMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _359.VirtualCylindricalGearSetISO10300MethodB1.TYPE not in self.wrapped.VirtualCylindricalGearSetMethodB1.__class__.__mro__:
            raise CastException('Failed to cast virtual_cylindrical_gear_set_method_b1 to VirtualCylindricalGearSetISO10300MethodB1. Expected: {}.'.format(self.wrapped.VirtualCylindricalGearSetMethodB1.__class__.__qualname__))

        return constructor.new_override(self.wrapped.VirtualCylindricalGearSetMethodB1.__class__)(self.wrapped.VirtualCylindricalGearSetMethodB1) if self.wrapped.VirtualCylindricalGearSetMethodB1 is not None else None

    @property
    def virtual_cylindrical_gear_set_method_b1_of_type_bevel_virtual_cylindrical_gear_set_iso10300_method_b1(self) -> '_345.BevelVirtualCylindricalGearSetISO10300MethodB1':
        '''BevelVirtualCylindricalGearSetISO10300MethodB1: 'VirtualCylindricalGearSetMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _345.BevelVirtualCylindricalGearSetISO10300MethodB1.TYPE not in self.wrapped.VirtualCylindricalGearSetMethodB1.__class__.__mro__:
            raise CastException('Failed to cast virtual_cylindrical_gear_set_method_b1 to BevelVirtualCylindricalGearSetISO10300MethodB1. Expected: {}.'.format(self.wrapped.VirtualCylindricalGearSetMethodB1.__class__.__qualname__))

        return constructor.new_override(self.wrapped.VirtualCylindricalGearSetMethodB1.__class__)(self.wrapped.VirtualCylindricalGearSetMethodB1) if self.wrapped.VirtualCylindricalGearSetMethodB1 is not None else None

    @property
    def virtual_cylindrical_gear_set_method_b1_of_type_hypoid_virtual_cylindrical_gear_set_iso10300_method_b1(self) -> '_348.HypoidVirtualCylindricalGearSetISO10300MethodB1':
        '''HypoidVirtualCylindricalGearSetISO10300MethodB1: 'VirtualCylindricalGearSetMethodB1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _348.HypoidVirtualCylindricalGearSetISO10300MethodB1.TYPE not in self.wrapped.VirtualCylindricalGearSetMethodB1.__class__.__mro__:
            raise CastException('Failed to cast virtual_cylindrical_gear_set_method_b1 to HypoidVirtualCylindricalGearSetISO10300MethodB1. Expected: {}.'.format(self.wrapped.VirtualCylindricalGearSetMethodB1.__class__.__qualname__))

        return constructor.new_override(self.wrapped.VirtualCylindricalGearSetMethodB1.__class__)(self.wrapped.VirtualCylindricalGearSetMethodB1) if self.wrapped.VirtualCylindricalGearSetMethodB1 is not None else None
