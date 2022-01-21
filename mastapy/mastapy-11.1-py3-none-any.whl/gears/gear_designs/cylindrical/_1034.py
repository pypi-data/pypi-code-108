'''_1034.py

TiffAnalysisSettings
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1333
from mastapy.gears.gear_designs.cylindrical import _1006
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_TIFF_ANALYSIS_SETTINGS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'TiffAnalysisSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('TiffAnalysisSettings',)


class TiffAnalysisSettings(_1382.IndependentReportablePropertiesBase['TiffAnalysisSettings']):
    '''TiffAnalysisSettings

    This is a mastapy class.
    '''

    TYPE = _TIFF_ANALYSIS_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TiffAnalysisSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_rotations_for_findley(self) -> 'int':
        '''int: 'NumberOfRotationsForFindley' is the original name of this property.'''

        return self.wrapped.NumberOfRotationsForFindley

    @number_of_rotations_for_findley.setter
    def number_of_rotations_for_findley(self, value: 'int'):
        self.wrapped.NumberOfRotationsForFindley = int(value) if value else 0

    @property
    def include_shot_peening(self) -> 'bool':
        '''bool: 'IncludeShotPeening' is the original name of this property.'''

        return self.wrapped.IncludeShotPeening

    @include_shot_peening.setter
    def include_shot_peening(self, value: 'bool'):
        self.wrapped.IncludeShotPeening = bool(value) if value else False

    @property
    def shot_peening_depth(self) -> 'float':
        '''float: 'ShotPeeningDepth' is the original name of this property.'''

        return self.wrapped.ShotPeeningDepth

    @shot_peening_depth.setter
    def shot_peening_depth(self, value: 'float'):
        self.wrapped.ShotPeeningDepth = float(value) if value else 0.0

    @property
    def shot_peening_factor(self) -> 'float':
        '''float: 'ShotPeeningFactor' is the original name of this property.'''

        return self.wrapped.ShotPeeningFactor

    @shot_peening_factor.setter
    def shot_peening_factor(self, value: 'float'):
        self.wrapped.ShotPeeningFactor = float(value) if value else 0.0

    @property
    def include_residual_stresses(self) -> 'bool':
        '''bool: 'IncludeResidualStresses' is the original name of this property.'''

        return self.wrapped.IncludeResidualStresses

    @include_residual_stresses.setter
    def include_residual_stresses(self, value: 'bool'):
        self.wrapped.IncludeResidualStresses = bool(value) if value else False

    @property
    def include_findley_analysis(self) -> 'bool':
        '''bool: 'IncludeFindleyAnalysis' is the original name of this property.'''

        return self.wrapped.IncludeFindleyAnalysis

    @include_findley_analysis.setter
    def include_findley_analysis(self, value: 'bool'):
        self.wrapped.IncludeFindleyAnalysis = bool(value) if value else False

    @property
    def strain_at_surface(self) -> 'float':
        '''float: 'StrainAtSurface' is the original name of this property.'''

        return self.wrapped.StrainAtSurface

    @strain_at_surface.setter
    def strain_at_surface(self, value: 'float'):
        self.wrapped.StrainAtSurface = float(value) if value else 0.0

    @property
    def strain_at_mid_case_depth(self) -> 'float':
        '''float: 'StrainAtMidCaseDepth' is the original name of this property.'''

        return self.wrapped.StrainAtMidCaseDepth

    @strain_at_mid_case_depth.setter
    def strain_at_mid_case_depth(self, value: 'float'):
        self.wrapped.StrainAtMidCaseDepth = float(value) if value else 0.0

    @property
    def measured_residual_stress_profile_property(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'MeasuredResidualStressProfileProperty' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.MeasuredResidualStressProfileProperty) if self.wrapped.MeasuredResidualStressProfileProperty is not None else None

    @measured_residual_stress_profile_property.setter
    def measured_residual_stress_profile_property(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.MeasuredResidualStressProfileProperty = value

    @property
    def surface_material_properties(self) -> '_1006.HardenedMaterialProperties':
        '''HardenedMaterialProperties: 'SurfaceMaterialProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1006.HardenedMaterialProperties)(self.wrapped.SurfaceMaterialProperties) if self.wrapped.SurfaceMaterialProperties is not None else None

    @property
    def core_material_properties(self) -> '_1006.HardenedMaterialProperties':
        '''HardenedMaterialProperties: 'CoreMaterialProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1006.HardenedMaterialProperties)(self.wrapped.CoreMaterialProperties) if self.wrapped.CoreMaterialProperties is not None else None
