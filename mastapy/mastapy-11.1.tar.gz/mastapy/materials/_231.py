'''_231.py

LubricantDefinition
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LUBRICANT_DEFINITION = python_net_import('SMT.MastaAPI.Materials', 'LubricantDefinition')


__docformat__ = 'restructuredtext en'
__all__ = ('LubricantDefinition',)


class LubricantDefinition(Enum):
    '''LubricantDefinition

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LUBRICANT_DEFINITION

    __hash__ = None

    STANDARD = 0
    AGMA_925A03 = 1
    VDI_27362014 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LubricantDefinition.__setattr__ = __enum_setattr
LubricantDefinition.__delattr__ = __enum_delattr
