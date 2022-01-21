'''_2331.py

RigidConnectorStiffnessType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RIGID_CONNECTOR_STIFFNESS_TYPE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'RigidConnectorStiffnessType')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidConnectorStiffnessType',)


class RigidConnectorStiffnessType(Enum):
    '''RigidConnectorStiffnessType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RIGID_CONNECTOR_STIFFNESS_TYPE

    __hash__ = None

    SIMPLE = 0
    SPECIFY_MATRIX = 1
    NONLINEAR = 2
    INDIVIDUAL_CONTACTS = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RigidConnectorStiffnessType.__setattr__ = __enum_setattr
RigidConnectorStiffnessType.__delattr__ = __enum_delattr
