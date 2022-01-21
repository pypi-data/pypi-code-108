'''_2069.py

StraightBevelGearMesh
'''


from mastapy.gears.gear_designs.straight_bevel import _923
from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets.gears import _2045
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'StraightBevelGearMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearMesh',)


class StraightBevelGearMesh(_2045.BevelGearMesh):
    '''StraightBevelGearMesh

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bevel_gear_mesh_design(self) -> '_923.StraightBevelGearMeshDesign':
        '''StraightBevelGearMeshDesign: 'BevelGearMeshDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_923.StraightBevelGearMeshDesign)(self.wrapped.BevelGearMeshDesign) if self.wrapped.BevelGearMeshDesign is not None else None

    @property
    def straight_bevel_gear_mesh_design(self) -> '_923.StraightBevelGearMeshDesign':
        '''StraightBevelGearMeshDesign: 'StraightBevelGearMeshDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_923.StraightBevelGearMeshDesign)(self.wrapped.StraightBevelGearMeshDesign) if self.wrapped.StraightBevelGearMeshDesign is not None else None
