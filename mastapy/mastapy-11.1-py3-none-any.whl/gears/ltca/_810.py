'''_810.py

UseAdvancedLTCAOptions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_USE_ADVANCED_LTCA_OPTIONS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'UseAdvancedLTCAOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('UseAdvancedLTCAOptions',)


class UseAdvancedLTCAOptions(Enum):
    '''UseAdvancedLTCAOptions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _USE_ADVANCED_LTCA_OPTIONS

    __hash__ = None

    YES = 0
    NO = 1
    SPECIFY_FOR_EACH_MESH = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


UseAdvancedLTCAOptions.__setattr__ = __enum_setattr
UseAdvancedLTCAOptions.__delattr__ = __enum_delattr
