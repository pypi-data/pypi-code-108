'''_1563.py

Severity
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SEVERITY = python_net_import('SMT.MastaAPI.Utility.ModelValidation', 'Severity')


__docformat__ = 'restructuredtext en'
__all__ = ('Severity',)


class Severity(Enum):
    '''Severity

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SEVERITY

    __hash__ = None

    INFORMATION = 1
    WARNING = 2
    ERROR = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Severity.__setattr__ = __enum_setattr
Severity.__delattr__ = __enum_delattr
