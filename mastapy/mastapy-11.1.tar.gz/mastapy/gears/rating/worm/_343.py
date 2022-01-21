'''_343.py

WormMeshDutyCycleRating
'''


from typing import List

from mastapy.gears.rating.worm import _339
from mastapy._internal import constructor, conversion
from mastapy.gears.rating import _331
from mastapy._internal.python_net import python_net_import

_WORM_MESH_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Worm', 'WormMeshDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('WormMeshDutyCycleRating',)


class WormMeshDutyCycleRating(_331.MeshDutyCycleRating):
    '''WormMeshDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _WORM_MESH_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormMeshDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def worm_mesh_ratings(self) -> 'List[_339.WormGearMeshRating]':
        '''List[WormGearMeshRating]: 'WormMeshRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshRatings, constructor.new(_339.WormGearMeshRating))
        return value
