'''_335.py

ZerolBevelGearMeshRating
'''


from typing import List

from mastapy.gears.gear_designs.zerol_bevel import _910
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.zerol_bevel import _336
from mastapy.gears.rating.bevel import _514
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_MESH_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.ZerolBevel', 'ZerolBevelGearMeshRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearMeshRating',)


class ZerolBevelGearMeshRating(_514.BevelGearMeshRating):
    '''ZerolBevelGearMeshRating

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_MESH_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearMeshRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def zerol_bevel_gear_mesh(self) -> '_910.ZerolBevelGearMeshDesign':
        '''ZerolBevelGearMeshDesign: 'ZerolBevelGearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_910.ZerolBevelGearMeshDesign)(self.wrapped.ZerolBevelGearMesh) if self.wrapped.ZerolBevelGearMesh is not None else None

    @property
    def zerol_bevel_gear_ratings(self) -> 'List[_336.ZerolBevelGearRating]':
        '''List[ZerolBevelGearRating]: 'ZerolBevelGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearRatings, constructor.new(_336.ZerolBevelGearRating))
        return value
