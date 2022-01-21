'''_232.py

LubricantDelivery
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LUBRICANT_DELIVERY = python_net_import('SMT.MastaAPI.Materials', 'LubricantDelivery')


__docformat__ = 'restructuredtext en'
__all__ = ('LubricantDelivery',)


class LubricantDelivery(Enum):
    '''LubricantDelivery

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LUBRICANT_DELIVERY

    __hash__ = None

    SEALED = 0
    SPLASH = 1
    FEED = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LubricantDelivery.__setattr__ = __enum_setattr
LubricantDelivery.__delattr__ = __enum_delattr
