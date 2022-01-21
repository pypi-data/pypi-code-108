'''_337.py

ZerolBevelGearSetRating
'''


from typing import List

from mastapy.gears.gear_designs.zerol_bevel import _911
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.zerol_bevel import _335, _336
from mastapy.gears.rating.bevel import _516
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_SET_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.ZerolBevel', 'ZerolBevelGearSetRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearSetRating',)


class ZerolBevelGearSetRating(_516.BevelGearSetRating):
    '''ZerolBevelGearSetRating

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_SET_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearSetRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def zerol_bevel_gear_set(self) -> '_911.ZerolBevelGearSetDesign':
        '''ZerolBevelGearSetDesign: 'ZerolBevelGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_911.ZerolBevelGearSetDesign)(self.wrapped.ZerolBevelGearSet) if self.wrapped.ZerolBevelGearSet is not None else None

    @property
    def zerol_bevel_mesh_ratings(self) -> 'List[_335.ZerolBevelGearMeshRating]':
        '''List[ZerolBevelGearMeshRating]: 'ZerolBevelMeshRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelMeshRatings, constructor.new(_335.ZerolBevelGearMeshRating))
        return value

    @property
    def zerol_bevel_gear_ratings(self) -> 'List[_336.ZerolBevelGearRating]':
        '''List[ZerolBevelGearRating]: 'ZerolBevelGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearRatings, constructor.new(_336.ZerolBevelGearRating))
        return value
