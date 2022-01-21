'''_290.py

CylindricalMisalignmentDataSource
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MISALIGNMENT_DATA_SOURCE = python_net_import('SMT.MastaAPI.Gears', 'CylindricalMisalignmentDataSource')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMisalignmentDataSource',)


class CylindricalMisalignmentDataSource(Enum):
    '''CylindricalMisalignmentDataSource

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CYLINDRICAL_MISALIGNMENT_DATA_SOURCE

    __hash__ = None

    STANDARD = 0
    USERSPECIFIED = 1
    SYSTEM_DEFLECTION = 2
    ADVANCED_SYSTEM_DEFLECTION = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CylindricalMisalignmentDataSource.__setattr__ = __enum_setattr
CylindricalMisalignmentDataSource.__delattr__ = __enum_delattr
