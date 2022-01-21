'''_2041.py

AGMAGleasonConicalGearMesh
'''


from mastapy.system_model.connections_and_sockets.gears import _2049
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'AGMAGleasonConicalGearMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMesh',)


class AGMAGleasonConicalGearMesh(_2049.ConicalGearMesh):
    '''AGMAGleasonConicalGearMesh

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
