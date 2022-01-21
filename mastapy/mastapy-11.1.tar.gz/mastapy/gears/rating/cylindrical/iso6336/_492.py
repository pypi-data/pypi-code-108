'''_492.py

ToothFlankFractureStressStepAtAnalysisPointN1457
'''


from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy._math.vector_2d import Vector2D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TOOTH_FLANK_FRACTURE_STRESS_STEP_AT_ANALYSIS_POINT_N1457 = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ToothFlankFractureStressStepAtAnalysisPointN1457')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothFlankFractureStressStepAtAnalysisPointN1457',)


class ToothFlankFractureStressStepAtAnalysisPointN1457(_0.APIBase):
    '''ToothFlankFractureStressStepAtAnalysisPointN1457

    This is a mastapy class.
    '''

    TYPE = _TOOTH_FLANK_FRACTURE_STRESS_STEP_AT_ANALYSIS_POINT_N1457

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothFlankFractureStressStepAtAnalysisPointN1457.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def equivalent_stress(self) -> 'float':
        '''float: 'EquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentStress

    @property
    def hydrostatic_pressure(self) -> 'float':
        '''float: 'HydrostaticPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HydrostaticPressure

    @property
    def fatigue_sensitivity_to_hydro_static_pressure(self) -> 'float':
        '''float: 'FatigueSensitivityToHydroStaticPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSensitivityToHydroStaticPressure

    @property
    def second_stress_invariant(self) -> 'float':
        '''float: 'SecondStressInvariant' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SecondStressInvariant

    @property
    def global_transverse_stress(self) -> 'float':
        '''float: 'GlobalTransverseStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GlobalTransverseStress

    @property
    def transverse_stress_due_to_normal_load(self) -> 'float':
        '''float: 'TransverseStressDueToNormalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseStressDueToNormalLoad

    @property
    def transverse_stress_due_to_friction(self) -> 'float':
        '''float: 'TransverseStressDueToFriction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseStressDueToFriction

    @property
    def global_normal_stress(self) -> 'float':
        '''float: 'GlobalNormalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GlobalNormalStress

    @property
    def normal_stress_due_to_normal_load(self) -> 'float':
        '''float: 'NormalStressDueToNormalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalStressDueToNormalLoad

    @property
    def normal_stress_due_to_friction(self) -> 'float':
        '''float: 'NormalStressDueToFriction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalStressDueToFriction

    @property
    def global_shear_stress(self) -> 'float':
        '''float: 'GlobalShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GlobalShearStress

    @property
    def shear_stress_due_to_normal_load(self) -> 'float':
        '''float: 'ShearStressDueToNormalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearStressDueToNormalLoad

    @property
    def shear_stress_due_to_friction(self) -> 'float':
        '''float: 'ShearStressDueToFriction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearStressDueToFriction

    @property
    def third_normal_stress(self) -> 'float':
        '''float: 'ThirdNormalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThirdNormalStress

    @property
    def first_hertzian_parameter(self) -> 'float':
        '''float: 'FirstHertzianParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FirstHertzianParameter

    @property
    def second_hertzian_parameter(self) -> 'float':
        '''float: 'SecondHertzianParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SecondHertzianParameter

    @property
    def contact_position_on_profile(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ContactPositionOnProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ContactPositionOnProfile) if self.wrapped.ContactPositionOnProfile is not None else None

    @property
    def relative_coordinates(self) -> 'Vector2D':
        '''Vector2D: 'RelativeCoordinates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.RelativeCoordinates)
        return value
