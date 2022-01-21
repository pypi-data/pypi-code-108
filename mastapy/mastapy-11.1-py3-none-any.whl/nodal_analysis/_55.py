'''_55.py

ElementOrder
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ELEMENT_ORDER = python_net_import('SMT.MastaAPI.NodalAnalysis', 'ElementOrder')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementOrder',)


class ElementOrder(Enum):
    '''ElementOrder

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ELEMENT_ORDER

    __hash__ = None

    LINEAR = 0
    QUADRATIC = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ElementOrder.__setattr__ = __enum_setattr
ElementOrder.__delattr__ = __enum_delattr
