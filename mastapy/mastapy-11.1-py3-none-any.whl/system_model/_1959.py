'''_1959.py

MeshStiffnessModel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MESH_STIFFNESS_MODEL = python_net_import('SMT.MastaAPI.SystemModel', 'MeshStiffnessModel')


__docformat__ = 'restructuredtext en'
__all__ = ('MeshStiffnessModel',)


class MeshStiffnessModel(Enum):
    '''MeshStiffnessModel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MESH_STIFFNESS_MODEL

    __hash__ = None

    CONSTANT_IN_LOA = 0
    ADVANCED_SYSTEM_DEFLECTION = 1
    ISO_SIMPLE_CONTINUOUS_MODEL = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MeshStiffnessModel.__setattr__ = __enum_setattr
MeshStiffnessModel.__delattr__ = __enum_delattr
