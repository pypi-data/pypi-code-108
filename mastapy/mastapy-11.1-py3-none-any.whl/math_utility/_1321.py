'''_1321.py

PIDControlUpdateMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PID_CONTROL_UPDATE_METHOD = python_net_import('SMT.MastaAPI.MathUtility', 'PIDControlUpdateMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('PIDControlUpdateMethod',)


class PIDControlUpdateMethod(Enum):
    '''PIDControlUpdateMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PID_CONTROL_UPDATE_METHOD

    __hash__ = None

    EACH_SOLVER_STEP = 0
    SAMPLE_TIME = 1
    CONTINUOUS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PIDControlUpdateMethod.__setattr__ = __enum_setattr
PIDControlUpdateMethod.__delattr__ = __enum_delattr
