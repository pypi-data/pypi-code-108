'''_319.py

AbstractGearMeshRating
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1160
from mastapy._internal.python_net import python_net_import

_ABSTRACT_GEAR_MESH_RATING = python_net_import('SMT.MastaAPI.Gears.Rating', 'AbstractGearMeshRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractGearMeshRating',)


class AbstractGearMeshRating(_1160.AbstractGearMeshAnalysis):
    '''AbstractGearMeshRating

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_GEAR_MESH_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractGearMeshRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def normalized_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForFatigue

    @property
    def normalized_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForStatic

    @property
    def mesh_efficiency(self) -> 'float':
        '''float: 'MeshEfficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshEfficiency
