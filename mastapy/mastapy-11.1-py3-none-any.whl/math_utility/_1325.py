'''_1325.py

ResultOptionsFor3DVector
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RESULT_OPTIONS_FOR_3D_VECTOR = python_net_import('SMT.MastaAPI.MathUtility', 'ResultOptionsFor3DVector')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultOptionsFor3DVector',)


class ResultOptionsFor3DVector(Enum):
    '''ResultOptionsFor3DVector

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RESULT_OPTIONS_FOR_3D_VECTOR

    __hash__ = None

    X = 0
    Y = 1
    Z = 2
    MAGNITUDE_XY = 3
    MAGNITUDE = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ResultOptionsFor3DVector.__setattr__ = __enum_setattr
ResultOptionsFor3DVector.__delattr__ = __enum_delattr
