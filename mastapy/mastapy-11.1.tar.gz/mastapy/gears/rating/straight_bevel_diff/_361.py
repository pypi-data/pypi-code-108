'''_361.py

StraightBevelDiffGearMeshRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.straight_bevel_diff import _919
from mastapy.gears.rating.straight_bevel_diff import _364, _362
from mastapy.gears.rating.conical import _499
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_MESH_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.StraightBevelDiff', 'StraightBevelDiffGearMeshRating')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearMeshRating',)


class StraightBevelDiffGearMeshRating(_499.ConicalGearMeshRating):
    '''StraightBevelDiffGearMeshRating

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_MESH_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearMeshRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_distribution_factor(self) -> 'float':
        '''float: 'LoadDistributionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactor

    @property
    def derating_factor(self) -> 'float':
        '''float: 'DeratingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DeratingFactor

    @property
    def inertia_factor_bending(self) -> 'float':
        '''float: 'InertiaFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaFactorBending

    @property
    def rating_result(self) -> 'str':
        '''str: 'RatingResult' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingResult

    @property
    def straight_bevel_diff_gear_mesh(self) -> '_919.StraightBevelDiffGearMeshDesign':
        '''StraightBevelDiffGearMeshDesign: 'StraightBevelDiffGearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_919.StraightBevelDiffGearMeshDesign)(self.wrapped.StraightBevelDiffGearMesh) if self.wrapped.StraightBevelDiffGearMesh is not None else None

    @property
    def meshed_gears(self) -> 'List[_364.StraightBevelDiffMeshedGearRating]':
        '''List[StraightBevelDiffMeshedGearRating]: 'MeshedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshedGears, constructor.new(_364.StraightBevelDiffMeshedGearRating))
        return value

    @property
    def gears_in_mesh(self) -> 'List[_364.StraightBevelDiffMeshedGearRating]':
        '''List[StraightBevelDiffMeshedGearRating]: 'GearsInMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearsInMesh, constructor.new(_364.StraightBevelDiffMeshedGearRating))
        return value

    @property
    def straight_bevel_diff_gear_ratings(self) -> 'List[_362.StraightBevelDiffGearRating]':
        '''List[StraightBevelDiffGearRating]: 'StraightBevelDiffGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelDiffGearRatings, constructor.new(_362.StraightBevelDiffGearRating))
        return value
