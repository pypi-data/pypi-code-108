'''_2317.py

BeltDriveType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BELT_DRIVE_TYPE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'BeltDriveType')


__docformat__ = 'restructuredtext en'
__all__ = ('BeltDriveType',)


class BeltDriveType(Enum):
    '''BeltDriveType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BELT_DRIVE_TYPE

    __hash__ = None

    PUSHBELT = 0
    PULLBELT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BeltDriveType.__setattr__ = __enum_setattr
BeltDriveType.__delattr__ = __enum_delattr
