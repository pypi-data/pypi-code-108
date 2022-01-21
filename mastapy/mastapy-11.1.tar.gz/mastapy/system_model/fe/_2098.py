'''_2098.py

AlignmentMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ALIGNMENT_METHOD = python_net_import('SMT.MastaAPI.SystemModel.FE', 'AlignmentMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('AlignmentMethod',)


class AlignmentMethod(Enum):
    '''AlignmentMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ALIGNMENT_METHOD

    __hash__ = None

    AUTO = 0
    MANUAL = 1
    DATUM = 2
    REPLACED_SHAFT = 3
    SHAFT = 4
    CONNECTABLE_COMPONENT = 5
    COMPONENT = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AlignmentMethod.__setattr__ = __enum_setattr
AlignmentMethod.__delattr__ = __enum_delattr
