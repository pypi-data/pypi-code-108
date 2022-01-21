'''_931.py

KlingelnbergCycloPalloidSpiralBevelGearMeshDesign
'''


from typing import List

from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _932, _930, _933
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.klingelnberg_conical import _939
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergSpiralBevel', 'KlingelnbergCycloPalloidSpiralBevelGearMeshDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearMeshDesign',)


class KlingelnbergCycloPalloidSpiralBevelGearMeshDesign(_939.KlingelnbergConicalGearMeshDesign):
    '''KlingelnbergCycloPalloidSpiralBevelGearMeshDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearMeshDesign.TYPE'):
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
    def klingelnberg_cyclo_palloid_spiral_bevel_gears(self) -> 'List[_930.KlingelnbergCycloPalloidSpiralBevelGearDesign]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearDesign]: 'KlingelnbergCycloPalloidSpiralBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGears, constructor.new(_930.KlingelnbergCycloPalloidSpiralBevelGearDesign))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshed_gears(self) -> 'List[_933.KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign]':
        '''List[KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign]: 'KlingelnbergCycloPalloidSpiralBevelMeshedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshedGears, constructor.new(_933.KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign))
        return value
