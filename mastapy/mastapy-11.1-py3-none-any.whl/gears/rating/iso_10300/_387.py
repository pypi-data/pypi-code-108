'''_387.py

Iso10300FinishingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ISO_10300_FINISHING_METHODS = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'Iso10300FinishingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('Iso10300FinishingMethods',)


class Iso10300FinishingMethods(Enum):
    '''Iso10300FinishingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ISO_10300_FINISHING_METHODS

    __hash__ = None

    NONE = 0
    LAPPED = 1
    GROUND = 2
    HARD_CUT = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Iso10300FinishingMethods.__setattr__ = __enum_setattr
Iso10300FinishingMethods.__delattr__ = __enum_delattr
