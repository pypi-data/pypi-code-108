'''_1326.py

RotationAxis
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROTATION_AXIS = python_net_import('SMT.MastaAPI.MathUtility', 'RotationAxis')


__docformat__ = 'restructuredtext en'
__all__ = ('RotationAxis',)


class RotationAxis(Enum):
    '''RotationAxis

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROTATION_AXIS

    __hash__ = None

    X_AXIS = 0
    Y_AXIS = 1
    Z_AXIS = 2
    USERSPECIFIED = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RotationAxis.__setattr__ = __enum_setattr
RotationAxis.__delattr__ = __enum_delattr
