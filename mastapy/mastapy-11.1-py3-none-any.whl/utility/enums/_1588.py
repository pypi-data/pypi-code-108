'''_1588.py

BearingForceArrowOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_FORCE_ARROW_OPTION = python_net_import('SMT.MastaAPI.Utility.Enums', 'BearingForceArrowOption')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingForceArrowOption',)


class BearingForceArrowOption(Enum):
    '''BearingForceArrowOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_FORCE_ARROW_OPTION

    __hash__ = None

    ELEMENT_FORCES = 0
    RESULTANT_FORCE = 1
    RESULTANT_FORCE_PER_ROW = 2
    DYNAMIC_EQUIVALENT_LOAD_ISO_2812007 = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingForceArrowOption.__setattr__ = __enum_setattr
BearingForceArrowOption.__delattr__ = __enum_delattr
