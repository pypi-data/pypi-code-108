'''_59.py

FEMeshingProblems
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FE_MESHING_PROBLEMS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'FEMeshingProblems')


__docformat__ = 'restructuredtext en'
__all__ = ('FEMeshingProblems',)


class FEMeshingProblems(Enum):
    '''FEMeshingProblems

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FE_MESHING_PROBLEMS

    __hash__ = None

    FREE_EDGE_TRIANGLES = 0
    INTERSECTING_TRIANGLES = 1
    NONMANIFOLD_TRIANGLES = 2
    INCONSISTENT_TRIANGLES = 3
    PENETRATING_TRIANGLES = 4
    UNRECOVERED_EDGES = 5
    UNRECOVERED_FACES = 6
    UNPURGED_POINTS = 7
    UNCONNECTED_POINTS = 8
    ZERO_ANGLE_FACES = 9
    NOT_INSERTED_NODES = 10


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FEMeshingProblems.__setattr__ = __enum_setattr
FEMeshingProblems.__delattr__ = __enum_delattr
