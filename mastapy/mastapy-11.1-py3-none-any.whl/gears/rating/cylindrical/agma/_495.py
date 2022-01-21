'''_495.py

AGMA2101GearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical import _429
from mastapy._internal.python_net import python_net_import

_AGMA2101_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.AGMA', 'AGMA2101GearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA2101GearSingleFlankRating',)


class AGMA2101GearSingleFlankRating(_429.CylindricalGearSingleFlankRating):
    '''AGMA2101GearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _AGMA2101_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA2101GearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tooth_form_factor(self) -> 'float':
        '''float: 'ToothFormFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothFormFactor

    @property
    def geometry_factor_j(self) -> 'float':
        '''float: 'GeometryFactorJ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorJ

    @property
    def backup_ratio(self) -> 'float':
        '''float: 'BackupRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BackupRatio

    @property
    def rim_thickness_factor(self) -> 'float':
        '''float: 'RimThicknessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThicknessFactor

    @property
    def hardness_ratio_factor(self) -> 'float':
        '''float: 'HardnessRatioFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HardnessRatioFactor

    @property
    def reliability_factor_contact(self) -> 'float':
        '''float: 'ReliabilityFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityFactorContact

    @property
    def reliability_factor_bending(self) -> 'float':
        '''float: 'ReliabilityFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityFactorBending

    @property
    def allowable_contact_load_factor(self) -> 'float':
        '''float: 'AllowableContactLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactLoadFactor

    @property
    def stress_cycle_factor_for_pitting(self) -> 'float':
        '''float: 'StressCycleFactorForPitting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCycleFactorForPitting

    @property
    def tolerance_diameter(self) -> 'float':
        '''float: 'ToleranceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToleranceDiameter

    @property
    def single_pitch_deviation_agma(self) -> 'float':
        '''float: 'SinglePitchDeviationAGMA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePitchDeviationAGMA

    @property
    def pitting_resistance_power_rating(self) -> 'float':
        '''float: 'PittingResistancePowerRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingResistancePowerRating

    @property
    def allowable_transmitted_power_for_pitting_resistance_at_unity_service_factor(self) -> 'float':
        '''float: 'AllowableTransmittedPowerForPittingResistanceAtUnityServiceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTransmittedPowerForPittingResistanceAtUnityServiceFactor

    @property
    def allowable_transmitted_power_for_bending_strength_at_unity_service_factor(self) -> 'float':
        '''float: 'AllowableTransmittedPowerForBendingStrengthAtUnityServiceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTransmittedPowerForBendingStrengthAtUnityServiceFactor

    @property
    def allowable_transmitted_power_for_bending_strength(self) -> 'float':
        '''float: 'AllowableTransmittedPowerForBendingStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTransmittedPowerForBendingStrength

    @property
    def allowable_unit_load_for_bending_strength(self) -> 'float':
        '''float: 'AllowableUnitLoadForBendingStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableUnitLoadForBendingStrength

    @property
    def load_angle(self) -> 'float':
        '''float: 'LoadAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadAngle

    @property
    def stress_correction_factor_agma(self) -> 'float':
        '''float: 'StressCorrectionFactorAGMA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFactorAGMA

    @property
    def helical_factor(self) -> 'float':
        '''float: 'HelicalFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelicalFactor

    @property
    def helix_angle_factor(self) -> 'float':
        '''float: 'HelixAngleFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleFactor

    @property
    def minimum_tolerance_diameter_for_the_agma_standard(self) -> 'float':
        '''float: 'MinimumToleranceDiameterForTheAGMAStandard' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumToleranceDiameterForTheAGMAStandard

    @property
    def maximum_tolerance_diameter_for_the_agma_standard(self) -> 'float':
        '''float: 'MaximumToleranceDiameterForTheAGMAStandard' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumToleranceDiameterForTheAGMAStandard

    @property
    def tooth_thickness_at_critical_section(self) -> 'float':
        '''float: 'ToothThicknessAtCriticalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothThicknessAtCriticalSection

    @property
    def height_of_lewis_parabola(self) -> 'float':
        '''float: 'HeightOfLewisParabola' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeightOfLewisParabola

    @property
    def root_fillet_radius(self) -> 'float':
        '''float: 'RootFilletRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadius

    @property
    def unit_load_for_bending_strength(self) -> 'float':
        '''float: 'UnitLoadForBendingStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UnitLoadForBendingStrength
