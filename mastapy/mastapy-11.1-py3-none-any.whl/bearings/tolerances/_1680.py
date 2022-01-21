'''_1680.py

TypeOfFit
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TYPE_OF_FIT = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'TypeOfFit')


__docformat__ = 'restructuredtext en'
__all__ = ('TypeOfFit',)


class TypeOfFit(Enum):
    '''TypeOfFit

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TYPE_OF_FIT

    __hash__ = None

    SPLINE = 0
    LINEAR = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TypeOfFit.__setattr__ = __enum_setattr
TypeOfFit.__delattr__ = __enum_delattr
