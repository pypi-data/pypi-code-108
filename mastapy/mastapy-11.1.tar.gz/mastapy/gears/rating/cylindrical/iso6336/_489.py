'''_489.py

ToothFlankFractureAnalysisPoint
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TOOTH_FLANK_FRACTURE_ANALYSIS_POINT = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ToothFlankFractureAnalysisPoint')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothFlankFractureAnalysisPoint',)


class ToothFlankFractureAnalysisPoint(_0.APIBase):
    '''ToothFlankFractureAnalysisPoint

    This is a mastapy class.
    '''

    TYPE = _TOOTH_FLANK_FRACTURE_ANALYSIS_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothFlankFractureAnalysisPoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def depth_from_surface(self) -> 'float':
        '''float: 'DepthFromSurface' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DepthFromSurface

    @property
    def normalised_depth_from_surface(self) -> 'float':
        '''float: 'NormalisedDepthFromSurface' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalisedDepthFromSurface

    @property
    def local_material_exposure(self) -> 'float':
        '''float: 'LocalMaterialExposure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalMaterialExposure

    @property
    def material_exposure_calibration_factor(self) -> 'float':
        '''float: 'MaterialExposureCalibrationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialExposureCalibrationFactor

    @property
    def local_occurring_equivalent_stress(self) -> 'float':
        '''float: 'LocalOccurringEquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalOccurringEquivalentStress

    @property
    def local_equivalent_stress_without_consideration_of_residual_stresses(self) -> 'float':
        '''float: 'LocalEquivalentStressWithoutConsiderationOfResidualStresses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalEquivalentStressWithoutConsiderationOfResidualStresses

    @property
    def influence_of_the_residual_stresses_on_the_local_equivalent_stress(self) -> 'float':
        '''float: 'InfluenceOfTheResidualStressesOnTheLocalEquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InfluenceOfTheResidualStressesOnTheLocalEquivalentStress

    @property
    def correction_factor_for_practice_oriented_calculation_approach_first(self) -> 'float':
        '''float: 'CorrectionFactorForPracticeOrientedCalculationApproachFirst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CorrectionFactorForPracticeOrientedCalculationApproachFirst

    @property
    def correction_factor_for_practice_oriented_calculation_approach_second(self) -> 'float':
        '''float: 'CorrectionFactorForPracticeOrientedCalculationApproachSecond' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CorrectionFactorForPracticeOrientedCalculationApproachSecond

    @property
    def hertzian_pressure_and_residual_stress_influence_factor(self) -> 'float':
        '''float: 'HertzianPressureAndResidualStressInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianPressureAndResidualStressInfluenceFactor

    @property
    def case_hardening_depth_influence_factor(self) -> 'float':
        '''float: 'CaseHardeningDepthInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CaseHardeningDepthInfluenceFactor

    @property
    def quasi_stationary_residual_stress(self) -> 'float':
        '''float: 'QuasiStationaryResidualStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.QuasiStationaryResidualStress

    @property
    def tangential_component_of_compressive_residual_stresses(self) -> 'float':
        '''float: 'TangentialComponentOfCompressiveResidualStresses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialComponentOfCompressiveResidualStresses

    @property
    def local_material_shear_strength(self) -> 'float':
        '''float: 'LocalMaterialShearStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalMaterialShearStrength

    @property
    def hardness_conversion_factor(self) -> 'float':
        '''float: 'HardnessConversionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HardnessConversionFactor

    @property
    def material_factor(self) -> 'float':
        '''float: 'MaterialFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialFactor

    @property
    def local_material_hardness(self) -> 'float':
        '''float: 'LocalMaterialHardness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalMaterialHardness
