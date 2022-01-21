'''_86.py

ValueInputOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_VALUE_INPUT_OPTION = python_net_import('SMT.MastaAPI.NodalAnalysis', 'ValueInputOption')


__docformat__ = 'restructuredtext en'
__all__ = ('ValueInputOption',)


class ValueInputOption(Enum):
    '''ValueInputOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _VALUE_INPUT_OPTION

    __hash__ = None

    CONSTANT = 0
    VARYING_WITH_TIME = 1
    VARYING_WITH_ANGLE = 2
    VARYING_WITH_POSITION = 3
    VARYING_WITH_ANGLE_AND_SPEED = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ValueInputOption.__setattr__ = __enum_setattr
ValueInputOption.__delattr__ = __enum_delattr
