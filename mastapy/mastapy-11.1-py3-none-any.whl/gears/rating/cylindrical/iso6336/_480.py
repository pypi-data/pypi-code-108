'''_480.py

ISO6336AbstractMetalGearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _478
from mastapy._internal.python_net import python_net_import

_ISO6336_ABSTRACT_METAL_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO6336AbstractMetalGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336AbstractMetalGearSingleFlankRating',)


class ISO6336AbstractMetalGearSingleFlankRating(_478.ISO6336AbstractGearSingleFlankRating):
    '''ISO6336AbstractMetalGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO6336_ABSTRACT_METAL_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336AbstractMetalGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def base_pitch_deviation(self) -> 'float':
        '''float: 'BasePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasePitchDeviation

    @property
    def moment_of_inertia_per_unit_face_width(self) -> 'float':
        '''float: 'MomentOfInertiaPerUnitFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MomentOfInertiaPerUnitFaceWidth

    @property
    def relative_individual_gear_mass_per_unit_face_width_referenced_to_line_of_action(self) -> 'float':
        '''float: 'RelativeIndividualGearMassPerUnitFaceWidthReferencedToLineOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeIndividualGearMassPerUnitFaceWidthReferencedToLineOfAction

    @property
    def life_factor_for_contact_stress(self) -> 'float':
        '''float: 'LifeFactorForContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForContactStress

    @property
    def life_factor_for_static_contact_stress(self) -> 'float':
        '''float: 'LifeFactorForStaticContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForStaticContactStress

    @property
    def life_factor_for_reference_contact_stress(self) -> 'float':
        '''float: 'LifeFactorForReferenceContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForReferenceContactStress

    @property
    def single_pair_tooth_contact_factor(self) -> 'float':
        '''float: 'SinglePairToothContactFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePairToothContactFactor

    @property
    def shot_peening_bending_stress_benefit(self) -> 'float':
        '''float: 'ShotPeeningBendingStressBenefit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShotPeeningBendingStressBenefit

    @property
    def life_factor_for_bending_stress(self) -> 'float':
        '''float: 'LifeFactorForBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForBendingStress

    @property
    def life_factor_for_static_bending_stress(self) -> 'float':
        '''float: 'LifeFactorForStaticBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForStaticBendingStress

    @property
    def life_factor_for_reference_bending_stress(self) -> 'float':
        '''float: 'LifeFactorForReferenceBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForReferenceBendingStress

    @property
    def relative_notch_sensitivity_factor(self) -> 'float':
        '''float: 'RelativeNotchSensitivityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeNotchSensitivityFactor

    @property
    def relative_surface_factor(self) -> 'float':
        '''float: 'RelativeSurfaceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceFactor

    @property
    def size_factor_tooth_root(self) -> 'float':
        '''float: 'SizeFactorToothRoot' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorToothRoot

    @property
    def relative_notch_sensitivity_factor_for_reference_stress(self) -> 'float':
        '''float: 'RelativeNotchSensitivityFactorForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeNotchSensitivityFactorForReferenceStress

    @property
    def relative_notch_sensitivity_factor_for_static_stress(self) -> 'float':
        '''float: 'RelativeNotchSensitivityFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeNotchSensitivityFactorForStaticStress

    @property
    def relative_surface_factor_for_reference_stress(self) -> 'float':
        '''float: 'RelativeSurfaceFactorForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceFactorForReferenceStress

    @property
    def relative_surface_factor_for_static_stress(self) -> 'float':
        '''float: 'RelativeSurfaceFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeSurfaceFactorForStaticStress

    @property
    def size_factor_for_reference_bending_stress(self) -> 'float':
        '''float: 'SizeFactorForReferenceBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorForReferenceBendingStress

    @property
    def static_size_factor_tooth_root(self) -> 'float':
        '''float: 'StaticSizeFactorToothRoot' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSizeFactorToothRoot

    @property
    def work_hardening_factor(self) -> 'float':
        '''float: 'WorkHardeningFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkHardeningFactor

    @property
    def lubricant_factor_for_static_stress(self) -> 'float':
        '''float: 'LubricantFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantFactorForStaticStress

    @property
    def lubricant_factor_for_reference_stress(self) -> 'float':
        '''float: 'LubricantFactorForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantFactorForReferenceStress

    @property
    def velocity_factor_for_static_stress(self) -> 'float':
        '''float: 'VelocityFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VelocityFactorForStaticStress

    @property
    def roughness_factor_for_reference_stress(self) -> 'float':
        '''float: 'RoughnessFactorForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactorForReferenceStress

    @property
    def roughness_factor_for_static_stress(self) -> 'float':
        '''float: 'RoughnessFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactorForStaticStress

    @property
    def velocity_factor_for_reference_stress(self) -> 'float':
        '''float: 'VelocityFactorForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VelocityFactorForReferenceStress

    @property
    def roughness_factor(self) -> 'float':
        '''float: 'RoughnessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactor

    @property
    def lubricant_factor(self) -> 'float':
        '''float: 'LubricantFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantFactor

    @property
    def velocity_factor(self) -> 'float':
        '''float: 'VelocityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VelocityFactor

    @property
    def size_factor(self) -> 'float':
        '''float: 'SizeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactor

    @property
    def size_factor_for_static_stress(self) -> 'float':
        '''float: 'SizeFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorForStaticStress

    @property
    def size_factor_for_reference_contact_stress(self) -> 'float':
        '''float: 'SizeFactorForReferenceContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorForReferenceContactStress

    @property
    def addendum_contact_ratio(self) -> 'float':
        '''float: 'AddendumContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumContactRatio

    @property
    def profile_form_deviation(self) -> 'float':
        '''float: 'ProfileFormDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormDeviation
