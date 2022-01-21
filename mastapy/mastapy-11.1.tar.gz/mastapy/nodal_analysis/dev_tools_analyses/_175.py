'''_175.py

RigidCouplingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RIGID_COUPLING_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'RigidCouplingType')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidCouplingType',)


class RigidCouplingType(Enum):
    '''RigidCouplingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RIGID_COUPLING_TYPE

    __hash__ = None

    KINEMATIC = 0
    DISTRIBUTING = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RigidCouplingType.__setattr__ = __enum_setattr
RigidCouplingType.__delattr__ = __enum_delattr
