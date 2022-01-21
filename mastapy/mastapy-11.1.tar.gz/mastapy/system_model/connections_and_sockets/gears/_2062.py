'''_2062.py

KlingelnbergCycloPalloidSpiralBevelGearMesh
'''


from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _931
from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets.gears import _2060
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'KlingelnbergCycloPalloidSpiralBevelGearMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearMesh',)


class KlingelnbergCycloPalloidSpiralBevelGearMesh(_2060.KlingelnbergCycloPalloidConicalGearMesh):
    '''KlingelnbergCycloPalloidSpiralBevelGearMesh

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_design(self) -> '_931.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearMeshDesign: 'KlingelnbergCycloPalloidSpiralBevelGearMeshDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_931.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign)(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign) if self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign is not None else None
