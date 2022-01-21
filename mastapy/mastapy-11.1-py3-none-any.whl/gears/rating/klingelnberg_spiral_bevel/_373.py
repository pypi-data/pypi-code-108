'''_373.py

KlingelnbergCycloPalloidSpiralBevelGearSetRating
'''


from typing import List

from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _932
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.klingelnberg_spiral_bevel import _371, _372
from mastapy.gears.rating.klingelnberg_conical import _379
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.KlingelnbergSpiralBevel', 'KlingelnbergCycloPalloidSpiralBevelGearSetRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearSetRating',)


class KlingelnbergCycloPalloidSpiralBevelGearSetRating(_379.KlingelnbergCycloPalloidConicalGearSetRating):
    '''KlingelnbergCycloPalloidSpiralBevelGearSetRating

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearSetRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set(self) -> '_932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetDesign: 'KlingelnbergCycloPalloidSpiralBevelGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_932.KlingelnbergCycloPalloidSpiralBevelGearSetDesign)(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSet) if self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearSet is not None else None

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_mesh_ratings(self) -> 'List[_371.KlingelnbergCycloPalloidSpiralBevelGearMeshRating]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshRating]: 'KlingelnbergCycloPalloidSpiralBevelMeshRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshRatings, constructor.new(_371.KlingelnbergCycloPalloidSpiralBevelGearMeshRating))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_ratings(self) -> 'List[_372.KlingelnbergCycloPalloidSpiralBevelGearRating]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearRating]: 'KlingelnbergCycloPalloidSpiralBevelGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearRatings, constructor.new(_372.KlingelnbergCycloPalloidSpiralBevelGearRating))
        return value
