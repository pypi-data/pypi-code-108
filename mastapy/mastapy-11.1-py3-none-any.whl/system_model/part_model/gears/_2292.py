'''_2292.py

WormGearSet
'''


from typing import List

from mastapy.gears.gear_designs.worm import _916
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.gears import _2291, _2272
from mastapy.system_model.connections_and_sockets.gears import _2071
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'WormGearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSet',)


class WormGearSet(_2272.GearSet):
    '''WormGearSet

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def active_gear_set_design(self) -> '_916.WormGearSetDesign':
        '''WormGearSetDesign: 'ActiveGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_916.WormGearSetDesign)(self.wrapped.ActiveGearSetDesign) if self.wrapped.ActiveGearSetDesign is not None else None

    @property
    def worm_gear_set_design(self) -> '_916.WormGearSetDesign':
        '''WormGearSetDesign: 'WormGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_916.WormGearSetDesign)(self.wrapped.WormGearSetDesign) if self.wrapped.WormGearSetDesign is not None else None

    @property
    def worm_gears(self) -> 'List[_2291.WormGear]':
        '''List[WormGear]: 'WormGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGears, constructor.new(_2291.WormGear))
        return value

    @property
    def worm_meshes(self) -> 'List[_2071.WormGearMesh]':
        '''List[WormGearMesh]: 'WormMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshes, constructor.new(_2071.WormGearMesh))
        return value
