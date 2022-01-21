'''_490.py

ToothFlankFractureAnalysisPointN1457
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_2d import Vector2D
from mastapy.gears.rating.cylindrical.iso6336 import _492
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TOOTH_FLANK_FRACTURE_ANALYSIS_POINT_N1457 = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ToothFlankFractureAnalysisPointN1457')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothFlankFractureAnalysisPointN1457',)


class ToothFlankFractureAnalysisPointN1457(_0.APIBase):
    '''ToothFlankFractureAnalysisPointN1457

    This is a mastapy class.
    '''

    TYPE = _TOOTH_FLANK_FRACTURE_ANALYSIS_POINT_N1457

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothFlankFractureAnalysisPointN1457.TYPE'):
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
    def fatigue_damage(self) -> 'float':
        '''float: 'FatigueDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueDamage

    @property
    def maximum_equivalent_stress(self) -> 'float':
        '''float: 'MaximumEquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEquivalentStress

    @property
    def local_permissible_shear_strength(self) -> 'float':
        '''float: 'LocalPermissibleShearStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalPermissibleShearStrength

    @property
    def hardness_conversion_factor(self) -> 'float':
        '''float: 'HardnessConversionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HardnessConversionFactor

    @property
    def local_material_hardness(self) -> 'float':
        '''float: 'LocalMaterialHardness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalMaterialHardness

    @property
    def tangential_component_of_compressive_residual_stresses(self) -> 'float':
        '''float: 'TangentialComponentOfCompressiveResidualStresses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialComponentOfCompressiveResidualStresses

    @property
    def coordinates(self) -> 'Vector2D':
        '''Vector2D: 'Coordinates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.Coordinates)
        return value

    @property
    def stress_analysis_with_maximum_equivalent_stress(self) -> '_492.ToothFlankFractureStressStepAtAnalysisPointN1457':
        '''ToothFlankFractureStressStepAtAnalysisPointN1457: 'StressAnalysisWithMaximumEquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_492.ToothFlankFractureStressStepAtAnalysisPointN1457)(self.wrapped.StressAnalysisWithMaximumEquivalentStress) if self.wrapped.StressAnalysisWithMaximumEquivalentStress is not None else None

    @property
    def stress_history(self) -> 'List[_492.ToothFlankFractureStressStepAtAnalysisPointN1457]':
        '''List[ToothFlankFractureStressStepAtAnalysisPointN1457]: 'StressHistory' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StressHistory, constructor.new(_492.ToothFlankFractureStressStepAtAnalysisPointN1457))
        return value
