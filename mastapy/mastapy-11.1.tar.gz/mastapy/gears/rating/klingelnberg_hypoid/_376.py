'''_376.py

KlingelnbergCycloPalloidHypoidGearSetRating
'''


from typing import List

from mastapy.gears.gear_designs.klingelnberg_hypoid import _936
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.klingelnberg_hypoid import _374, _375
from mastapy.gears.rating.klingelnberg_conical import _379
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.KlingelnbergHypoid', 'KlingelnbergCycloPalloidHypoidGearSetRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetRating',)


class KlingelnbergCycloPalloidHypoidGearSetRating(_379.KlingelnbergCycloPalloidConicalGearSetRating):
    '''KlingelnbergCycloPalloidHypoidGearSetRating

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set(self) -> '_936.KlingelnbergCycloPalloidHypoidGearSetDesign':
        '''KlingelnbergCycloPalloidHypoidGearSetDesign: 'KlingelnbergCycloPalloidHypoidGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_936.KlingelnbergCycloPalloidHypoidGearSetDesign)(self.wrapped.KlingelnbergCycloPalloidHypoidGearSet) if self.wrapped.KlingelnbergCycloPalloidHypoidGearSet is not None else None

    @property
    def klingelnberg_cyclo_palloid_hypoid_mesh_ratings(self) -> 'List[_374.KlingelnbergCycloPalloidHypoidGearMeshRating]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshRating]: 'KlingelnbergCycloPalloidHypoidMeshRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshRatings, constructor.new(_374.KlingelnbergCycloPalloidHypoidGearMeshRating))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_ratings(self) -> 'List[_375.KlingelnbergCycloPalloidHypoidGearRating]':
        '''List[KlingelnbergCycloPalloidHypoidGearRating]: 'KlingelnbergCycloPalloidHypoidGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearRatings, constructor.new(_375.KlingelnbergCycloPalloidHypoidGearRating))
        return value
