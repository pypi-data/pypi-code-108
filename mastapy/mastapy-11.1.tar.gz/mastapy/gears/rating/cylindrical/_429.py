'''_429.py

CylindricalGearSingleFlankRating
'''


from mastapy.materials import _243
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.rating.cylindrical import _424
from mastapy.gears.rating import _330
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSingleFlankRating',)


class CylindricalGearSingleFlankRating(_330.GearSingleFlankRating):
    '''CylindricalGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def metal_plastic(self) -> '_243.MetalPlasticType':
        '''MetalPlasticType: 'MetalPlastic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.MetalPlastic)
        return constructor.new(_243.MetalPlasticType)(value) if value is not None else None

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngle

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngle

    @property
    def pitch_diameter(self) -> 'float':
        '''float: 'PitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDiameter

    @property
    def combined_tip_relief(self) -> 'float':
        '''float: 'CombinedTipRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedTipRelief

    @property
    def base_diameter(self) -> 'float':
        '''float: 'BaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameter

    @property
    def rim_thickness(self) -> 'float':
        '''float: 'RimThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThickness

    @property
    def tooth_root_chord_at_critical_section(self) -> 'float':
        '''float: 'ToothRootChordAtCriticalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordAtCriticalSection

    @property
    def bending_moment_arm(self) -> 'float':
        '''float: 'BendingMomentArm' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingMomentArm

    @property
    def root_fillet_radius(self) -> 'float':
        '''float: 'RootFilletRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadius

    @property
    def flank_roughness_rz(self) -> 'float':
        '''float: 'FlankRoughnessRz' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlankRoughnessRz

    @property
    def fillet_roughness_rz(self) -> 'float':
        '''float: 'FilletRoughnessRz' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilletRoughnessRz

    @property
    def tooth_passing_speed(self) -> 'float':
        '''float: 'ToothPassingSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothPassingSpeed

    @property
    def gear_rotation_speed(self) -> 'float':
        '''float: 'GearRotationSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearRotationSpeed

    @property
    def normal_module(self) -> 'float':
        '''float: 'NormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalModule

    @property
    def transverse_pressure_angle(self) -> 'float':
        '''float: 'TransversePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePressureAngle

    @property
    def base_helix_angle(self) -> 'float':
        '''float: 'BaseHelixAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseHelixAngle

    @property
    def base_transverse_pitch(self) -> 'float':
        '''float: 'BaseTransversePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseTransversePitch

    @property
    def normal_base_pitch(self) -> 'float':
        '''float: 'NormalBasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalBasePitch

    @property
    def angular_velocity(self) -> 'float':
        '''float: 'AngularVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularVelocity

    @property
    def contact_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'ContactSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactSafetyFactorForFatigue

    @property
    def bending_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'BendingSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingSafetyFactorForFatigue

    @property
    def safety_factor_wear(self) -> 'float':
        '''float: 'SafetyFactorWear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorWear

    @property
    def reliability_contact(self) -> 'float':
        '''float: 'ReliabilityContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityContact

    @property
    def reliability_bending(self) -> 'float':
        '''float: 'ReliabilityBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityBending

    @property
    def damage_contact(self) -> 'float':
        '''float: 'DamageContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageContact

    @property
    def static_safety_factor_contact(self) -> 'float':
        '''float: 'StaticSafetyFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSafetyFactorContact

    @property
    def damage_bending(self) -> 'float':
        '''float: 'DamageBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageBending

    @property
    def static_safety_factor_bending(self) -> 'float':
        '''float: 'StaticSafetyFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSafetyFactorBending

    @property
    def damage_wear(self) -> 'float':
        '''float: 'DamageWear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageWear

    @property
    def thermal_contact_coefficient_for_report(self) -> 'float':
        '''float: 'ThermalContactCoefficientForReport' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalContactCoefficientForReport

    @property
    def contact_stress_source(self) -> 'str':
        '''str: 'ContactStressSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactStressSource

    @property
    def tooth_root_stress_source(self) -> 'str':
        '''str: 'ToothRootStressSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStressSource

    @property
    def pitting_stress_limit(self) -> 'float':
        '''float: 'PittingStressLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingStressLimit

    @property
    def pitting_stress_limit_for_reference_stress(self) -> 'float':
        '''float: 'PittingStressLimitForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingStressLimitForReferenceStress

    @property
    def pitting_stress_limit_for_static_stress(self) -> 'float':
        '''float: 'PittingStressLimitForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingStressLimitForStaticStress

    @property
    def tooth_root_stress_limit_for_static_stress(self) -> 'float':
        '''float: 'ToothRootStressLimitForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStressLimitForStaticStress

    @property
    def tooth_root_stress_limit_for_reference_stress(self) -> 'float':
        '''float: 'ToothRootStressLimitForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStressLimitForReferenceStress

    @property
    def tooth_root_stress_limit(self) -> 'float':
        '''float: 'ToothRootStressLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStressLimit

    @property
    def tooth_root_stress(self) -> 'float':
        '''float: 'ToothRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootStress

    @property
    def calculated_contact_stress(self) -> 'float':
        '''float: 'CalculatedContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedContactStress

    @property
    def permissible_contact_stress(self) -> 'float':
        '''float: 'PermissibleContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContactStress

    @property
    def permissible_contact_stress_for_static_stress(self) -> 'float':
        '''float: 'PermissibleContactStressForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContactStressForStaticStress

    @property
    def permissible_contact_stress_for_reference_stress(self) -> 'float':
        '''float: 'PermissibleContactStressForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContactStressForReferenceStress

    @property
    def permissible_tooth_root_bending_stress(self) -> 'float':
        '''float: 'PermissibleToothRootBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleToothRootBendingStress

    @property
    def permissible_tooth_root_bending_stress_for_static_stress(self) -> 'float':
        '''float: 'PermissibleToothRootBendingStressForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleToothRootBendingStressForStaticStress

    @property
    def permissible_tooth_root_bending_stress_for_reference_stress(self) -> 'float':
        '''float: 'PermissibleToothRootBendingStressForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleToothRootBendingStressForReferenceStress

    @property
    def permissible_linear_wear(self) -> 'float':
        '''float: 'PermissibleLinearWear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleLinearWear

    @property
    def averaged_linear_wear(self) -> 'float':
        '''float: 'AveragedLinearWear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AveragedLinearWear

    @property
    def minimum_factor_of_safety_pitting_fatigue(self) -> 'float':
        '''float: 'MinimumFactorOfSafetyPittingFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFactorOfSafetyPittingFatigue

    @property
    def minimum_factor_of_safety_bending_fatigue(self) -> 'float':
        '''float: 'MinimumFactorOfSafetyBendingFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFactorOfSafetyBendingFatigue

    @property
    def allowable_stress_number_contact(self) -> 'float':
        '''float: 'AllowableStressNumberContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressNumberContact

    @property
    def allowable_stress_number_bending(self) -> 'float':
        '''float: 'AllowableStressNumberBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressNumberBending

    @property
    def nominal_stress_number_bending(self) -> 'float':
        '''float: 'NominalStressNumberBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalStressNumberBending

    @property
    def reversed_bending_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReversedBendingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReversedBendingFactor) if self.wrapped.ReversedBendingFactor is not None else None

    @property
    def life_factor_for_contact_stress(self) -> 'float':
        '''float: 'LifeFactorForContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorForContactStress

    @property
    def stress_cycle_factor_bending(self) -> 'float':
        '''float: 'StressCycleFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCycleFactorBending

    @property
    def size_factor_contact(self) -> 'float':
        '''float: 'SizeFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SizeFactorContact

    @property
    def rim_thickness_factor(self) -> 'float':
        '''float: 'RimThicknessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThicknessFactor

    @property
    def welding_structural_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'WeldingStructuralFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.WeldingStructuralFactor) if self.wrapped.WeldingStructuralFactor is not None else None

    @property
    def rim_thickness_over_normal_module(self) -> 'float':
        '''float: 'RimThicknessOverNormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThicknessOverNormalModule

    @property
    def transverse_pitch(self) -> 'float':
        '''float: 'TransversePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePitch

    @property
    def axial_pitch(self) -> 'float':
        '''float: 'AxialPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialPitch

    @property
    def transverse_module(self) -> 'float':
        '''float: 'TransverseModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseModule

    @property
    def normal_pitch(self) -> 'float':
        '''float: 'NormalPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPitch

    @property
    def geometry_data_source_for_rating(self) -> '_424.CylindricalGearRatingGeometryDataSource':
        '''CylindricalGearRatingGeometryDataSource: 'GeometryDataSourceForRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.GeometryDataSourceForRating)
        return constructor.new(_424.CylindricalGearRatingGeometryDataSource)(value) if value is not None else None
