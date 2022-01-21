'''_1152.py

ConicalMeshFEModel
'''


from mastapy.gears.fe_model import _1145
from mastapy._internal.python_net import python_net_import

_CONICAL_MESH_FE_MODEL = python_net_import('SMT.MastaAPI.Gears.FEModel.Conical', 'ConicalMeshFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshFEModel',)


class ConicalMeshFEModel(_1145.GearMeshFEModel):
    '''ConicalMeshFEModel

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESH_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshFEModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
