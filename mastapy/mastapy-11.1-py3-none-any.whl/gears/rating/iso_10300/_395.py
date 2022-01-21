'''_395.py

ISO10300SingleFlankRating
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.rating.conical import _503
from mastapy.gears.rating.virtual_cylindrical_gears import _355
from mastapy._internal.python_net import python_net_import

_ISO10300_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ISO10300SingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO10300SingleFlankRating',)


T = TypeVar('T', bound='_355.VirtualCylindricalGearBasic')


class ISO10300SingleFlankRating(_503.ConicalGearSingleFlankRating, Generic[T]):
    '''ISO10300SingleFlankRating

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _ISO10300_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO10300SingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mean_pitch_diameter(self) -> 'float':
        '''float: 'MeanPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanPitchDiameter

    @property
    def nominal_tangential_force_of_bevel_gears(self) -> 'float':
        '''float: 'NominalTangentialForceOfBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTangentialForceOfBevelGears

    @property
    def nominal_torque(self) -> 'float':
        '''float: 'NominalTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTorque

    @property
    def nominal_power(self) -> 'float':
        '''float: 'NominalPower' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalPower

    @property
    def nominal_tangential_speed_at_mean_point(self) -> 'float':
        '''float: 'NominalTangentialSpeedAtMeanPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTangentialSpeedAtMeanPoint

    @property
    def relative_mass_per_unit_face_width_reference_to_line_of_action(self) -> 'float':
        '''float: 'RelativeMassPerUnitFaceWidthReferenceToLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMassPerUnitFaceWidthReferenceToLineOfAction

    @property
    def single_pitch_deviation(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SinglePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SinglePitchDeviation) if self.wrapped.SinglePitchDeviation is not None else None

    @property
    def allowable_contact_stress_number(self) -> 'float':
        '''float: 'AllowableContactStressNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactStressNumber

    @property
    def allowable_stress_number_bending(self) -> 'float':
        '''float: 'AllowableStressNumberBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressNumberBending

    @property
    def relative_surface_condition_factor(self) -> 'float':
        '''float: 'RelativeSurfaceConditionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceConditionFactor

    @property
    def lubricant_factor_method_b(self) -> 'float':
        '''float: 'LubricantFactorMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantFactorMethodB

    @property
    def constant_lubricant_film_factor_czl_method_b(self) -> 'float':
        '''float: 'ConstantLubricantFilmFactorCZLMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConstantLubricantFilmFactorCZLMethodB

    @property
    def speed_factor_method_b(self) -> 'float':
        '''float: 'SpeedFactorMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpeedFactorMethodB

    @property
    def constant_speed_factor_czv_method_b(self) -> 'float':
        '''float: 'ConstantSpeedFactorCZVMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConstantSpeedFactorCZVMethodB

    @property
    def roughness_factor_for_contact_stress_method_b(self) -> 'float':
        '''float: 'RoughnessFactorForContactStressMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactorForContactStressMethodB

    @property
    def constant_roughness_factor_czr_method_b(self) -> 'float':
        '''float: 'ConstantRoughnessFactorCZRMethodB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConstantRoughnessFactorCZRMethodB

    @property
    def product_of_lubricant_film_influence_factors(self) -> 'float':
        '''float: 'ProductOfLubricantFilmInfluenceFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProductOfLubricantFilmInfluenceFactors

    @property
    def work_hardening_factor(self) -> 'float':
        '''float: 'WorkHardeningFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkHardeningFactor

    @property
    def life_factor_for_contact_stress(self) -> 'float':
        '''float: 'LifeFactorForContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForContactStress

    @property
    def size_factor(self) -> 'float':
        '''float: 'SizeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactor

    @property
    def size_factor_for_structural_and_through_hardened_steels_spheroidal_cast_iron_perlitic_malleable_cast_iron(self) -> 'float':
        '''float: 'SizeFactorForStructuralAndThroughHardenedSteelsSpheroidalCastIronPerliticMalleableCastIron' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorForStructuralAndThroughHardenedSteelsSpheroidalCastIronPerliticMalleableCastIron

    @property
    def size_factor_for_case_flame_induction_hardened_steels_nitrided_or_nitro_carburized_steels(self) -> 'float':
        '''float: 'SizeFactorForCaseFlameInductionHardenedSteelsNitridedOrNitroCarburizedSteels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorForCaseFlameInductionHardenedSteelsNitridedOrNitroCarburizedSteels

    @property
    def size_factor_for_grey_cast_iron_and_spheroidal_cast_iron(self) -> 'float':
        '''float: 'SizeFactorForGreyCastIronAndSpheroidalCastIron' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorForGreyCastIronAndSpheroidalCastIron

    @property
    def life_factor_for_root_stress(self) -> 'float':
        '''float: 'LifeFactorForRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForRootStress
