'''_943.py

HypoidGearMeshDesign
'''


from typing import List

from mastapy.gears.gear_designs.hypoid import _944, _942, _945
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.agma_gleason_conical import _1141
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_MESH_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Hypoid', 'HypoidGearMeshDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearMeshDesign',)


class HypoidGearMeshDesign(_1141.AGMAGleasonConicalGearMeshDesign):
    '''HypoidGearMeshDesign

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_MESH_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearMeshDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hypoid_gear_set(self) -> '_944.HypoidGearSetDesign':
        '''HypoidGearSetDesign: 'HypoidGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_944.HypoidGearSetDesign)(self.wrapped.HypoidGearSet) if self.wrapped.HypoidGearSet is not None else None

    @property
    def hypoid_gears(self) -> 'List[_942.HypoidGearDesign]':
        '''List[HypoidGearDesign]: 'HypoidGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGears, constructor.new(_942.HypoidGearDesign))
        return value

    @property
    def hypoid_meshed_gears(self) -> 'List[_945.HypoidMeshedGearDesign]':
        '''List[HypoidMeshedGearDesign]: 'HypoidMeshedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshedGears, constructor.new(_945.HypoidMeshedGearDesign))
        return value
