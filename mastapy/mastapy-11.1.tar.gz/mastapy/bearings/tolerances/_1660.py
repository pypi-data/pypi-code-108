'''_1660.py

BearingToleranceDefinitionOptions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_TOLERANCE_DEFINITION_OPTIONS = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'BearingToleranceDefinitionOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingToleranceDefinitionOptions',)


class BearingToleranceDefinitionOptions(Enum):
    '''BearingToleranceDefinitionOptions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_TOLERANCE_DEFINITION_OPTIONS

    __hash__ = None

    CLASSES = 0
    VALUES = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingToleranceDefinitionOptions.__setattr__ = __enum_setattr
BearingToleranceDefinitionOptions.__delattr__ = __enum_delattr
