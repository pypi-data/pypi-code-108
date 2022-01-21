'''_2071.py

WormGearMesh
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.worm import _915
from mastapy.system_model.connections_and_sockets.gears import _2055
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'WormGearMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearMesh',)


class WormGearMesh(_2055.GearMesh):
    '''WormGearMesh

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def meshing_angle(self) -> 'float':
        '''float: 'MeshingAngle' is the original name of this property.'''

        return self.wrapped.MeshingAngle

    @meshing_angle.setter
    def meshing_angle(self, value: 'float'):
        self.wrapped.MeshingAngle = float(value) if value else 0.0

    @property
    def worm_gear_mesh_design(self) -> '_915.WormGearMeshDesign':
        '''WormGearMeshDesign: 'WormGearMeshDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_915.WormGearMeshDesign)(self.wrapped.WormGearMeshDesign) if self.wrapped.WormGearMeshDesign is not None else None
