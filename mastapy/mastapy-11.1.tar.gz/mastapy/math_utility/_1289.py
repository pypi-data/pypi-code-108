'''_1289.py

AlignmentAxis
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ALIGNMENT_AXIS = python_net_import('SMT.MastaAPI.MathUtility', 'AlignmentAxis')


__docformat__ = 'restructuredtext en'
__all__ = ('AlignmentAxis',)


class AlignmentAxis(Enum):
    '''AlignmentAxis

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ALIGNMENT_AXIS

    __hash__ = None

    XAXIS_PARALLEL = 0
    XAXIS_ANTIPARALLEL = 1
    YAXIS_PARALLEL = 2
    YAXIS_ANTIPARALLEL = 3
    ZAXIS_PARALLEL = 4
    ZAXIS_ANTIPARALLEL = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AlignmentAxis.__setattr__ = __enum_setattr
AlignmentAxis.__delattr__ = __enum_delattr
