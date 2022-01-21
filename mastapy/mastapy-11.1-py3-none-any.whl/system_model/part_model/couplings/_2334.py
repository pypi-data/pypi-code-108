'''_2334.py

RigidConnectorToothSpacingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RIGID_CONNECTOR_TOOTH_SPACING_TYPE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'RigidConnectorToothSpacingType')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidConnectorToothSpacingType',)


class RigidConnectorToothSpacingType(Enum):
    '''RigidConnectorToothSpacingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RIGID_CONNECTOR_TOOTH_SPACING_TYPE

    __hash__ = None

    EQUALLYSPACED_TEETH = 0
    CUSTOM_SPACING_OF_TEETH = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RigidConnectorToothSpacingType.__setattr__ = __enum_setattr
RigidConnectorToothSpacingType.__delattr__ = __enum_delattr
