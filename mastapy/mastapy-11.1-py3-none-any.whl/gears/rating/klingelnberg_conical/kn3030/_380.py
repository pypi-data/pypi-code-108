'''_380.py

KlingelnbergConicalMeshSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import _353
from mastapy.gears.rating import _332
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CONICAL_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.KlingelnbergConical.KN3030', 'KlingelnbergConicalMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergConicalMeshSingleFlankRating',)


class KlingelnbergConicalMeshSingleFlankRating(_332.MeshSingleFlankRating):
    '''KlingelnbergConicalMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CONICAL_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergConicalMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating_standard_name(self) -> 'str':
        '''str: 'RatingStandardName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingStandardName

    @property
    def application_factor(self) -> 'float':
        '''float: 'ApplicationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ApplicationFactor

    @property
    def load_distribution_factor_longitudinal(self) -> 'float':
        '''float: 'LoadDistributionFactorLongitudinal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactorLongitudinal

    @property
    def running_in_allowance(self) -> 'float':
        '''float: 'RunningInAllowance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunningInAllowance

    @property
    def helical_load_distribution_factor_scuffing(self) -> 'float':
        '''float: 'HelicalLoadDistributionFactorScuffing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelicalLoadDistributionFactorScuffing

    @property
    def single_meshing_factor_pinion(self) -> 'float':
        '''float: 'SingleMeshingFactorPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingleMeshingFactorPinion

    @property
    def single_meshing_factor_wheel(self) -> 'float':
        '''float: 'SingleMeshingFactorWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingleMeshingFactorWheel

    @property
    def zone_factor(self) -> 'float':
        '''float: 'ZoneFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ZoneFactor

    @property
    def elasticity_factor(self) -> 'float':
        '''float: 'ElasticityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticityFactor

    @property
    def contact_ratio_factor_pitting(self) -> 'float':
        '''float: 'ContactRatioFactorPitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioFactorPitting

    @property
    def helix_angle_factor_pitting(self) -> 'float':
        '''float: 'HelixAngleFactorPitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleFactorPitting

    @property
    def bevel_gear_factor_pitting(self) -> 'float':
        '''float: 'BevelGearFactorPitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BevelGearFactorPitting

    @property
    def lubrication_speed_roughness_factor_product(self) -> 'float':
        '''float: 'LubricationSpeedRoughnessFactorProduct' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricationSpeedRoughnessFactorProduct

    @property
    def contact_stress_limit(self) -> 'float':
        '''float: 'ContactStressLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressLimit

    @property
    def allowable_contact_stress_number(self) -> 'float':
        '''float: 'AllowableContactStressNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactStressNumber

    @property
    def size_factor(self) -> 'float':
        '''float: 'SizeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactor

    @property
    def contact_stress_safety_factor(self) -> 'float':
        '''float: 'ContactStressSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressSafetyFactor

    @property
    def stress_correction_factor(self) -> 'float':
        '''float: 'StressCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFactor

    @property
    def contact_ratio_factor_bending(self) -> 'float':
        '''float: 'ContactRatioFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioFactorBending

    @property
    def helix_angle_factor_bending(self) -> 'float':
        '''float: 'HelixAngleFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleFactorBending

    @property
    def bevel_gear_factor_bending(self) -> 'float':
        '''float: 'BevelGearFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BevelGearFactorBending

    @property
    def alternating_load_factor(self) -> 'float':
        '''float: 'AlternatingLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AlternatingLoadFactor

    @property
    def lubrication_factor(self) -> 'float':
        '''float: 'LubricationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricationFactor

    @property
    def meshing_factor(self) -> 'float':
        '''float: 'MeshingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshingFactor

    @property
    def tip_relief_factor(self) -> 'float':
        '''float: 'TipReliefFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipReliefFactor

    @property
    def sump_temperature(self) -> 'float':
        '''float: 'SumpTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumpTemperature

    @property
    def dynamic_viscosity_at_sump_temperature(self) -> 'float':
        '''float: 'DynamicViscosityAtSumpTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicViscosityAtSumpTemperature

    @property
    def roughness_factor(self) -> 'float':
        '''float: 'RoughnessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactor

    @property
    def pinion_torque_of_test_gear(self) -> 'float':
        '''float: 'PinionTorqueOfTestGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionTorqueOfTestGear

    @property
    def material_factor(self) -> 'float':
        '''float: 'MaterialFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialFactor

    @property
    def rated_tangential_force(self) -> 'float':
        '''float: 'RatedTangentialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatedTangentialForce

    @property
    def tangential_speed(self) -> 'float':
        '''float: 'TangentialSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialSpeed

    @property
    def specific_line_load(self) -> 'float':
        '''float: 'SpecificLineLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpecificLineLoad

    @property
    def contact_stress(self) -> 'float':
        '''float: 'ContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStress

    @property
    def relating_factor_for_the_mass_temperature(self) -> 'float':
        '''float: 'RelatingFactorForTheMassTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelatingFactorForTheMassTemperature

    @property
    def operating_oil_temperature(self) -> 'float':
        '''float: 'OperatingOilTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OperatingOilTemperature

    @property
    def actual_integral_temperature(self) -> 'float':
        '''float: 'ActualIntegralTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualIntegralTemperature

    @property
    def allowable_scuffing_temperature(self) -> 'float':
        '''float: 'AllowableScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableScuffingTemperature

    @property
    def safety_factor_for_scuffing(self) -> 'float':
        '''float: 'SafetyFactorForScuffing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForScuffing

    @property
    def virtual_cylindrical_gear_set(self) -> '_353.KlingelnbergVirtualCylindricalGearSet':
        '''KlingelnbergVirtualCylindricalGearSet: 'VirtualCylindricalGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_353.KlingelnbergVirtualCylindricalGearSet)(self.wrapped.VirtualCylindricalGearSet) if self.wrapped.VirtualCylindricalGearSet is not None else None
