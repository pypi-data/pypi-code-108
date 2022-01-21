'''_1195.py

FitTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FIT_TYPES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'FitTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('FitTypes',)


class FitTypes(Enum):
    '''FitTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FIT_TYPES

    __hash__ = None

    SIDE_FIT = 0
    MAJOR_DIAMETER_FIT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FitTypes.__setattr__ = __enum_setattr
FitTypes.__delattr__ = __enum_delattr
