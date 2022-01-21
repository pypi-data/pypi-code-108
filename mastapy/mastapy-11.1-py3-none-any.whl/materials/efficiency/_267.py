'''_267.py

OilPumpDriveType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_OIL_PUMP_DRIVE_TYPE = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'OilPumpDriveType')


__docformat__ = 'restructuredtext en'
__all__ = ('OilPumpDriveType',)


class OilPumpDriveType(Enum):
    '''OilPumpDriveType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _OIL_PUMP_DRIVE_TYPE

    __hash__ = None

    MECHANICAL = 0
    ELECTRICAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


OilPumpDriveType.__setattr__ = __enum_setattr
OilPumpDriveType.__delattr__ = __enum_delattr
