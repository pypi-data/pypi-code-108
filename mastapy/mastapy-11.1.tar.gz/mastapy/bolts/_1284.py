'''_1284.py

ThreadTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_THREAD_TYPES = python_net_import('SMT.MastaAPI.Bolts', 'ThreadTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('ThreadTypes',)


class ThreadTypes(Enum):
    '''ThreadTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _THREAD_TYPES

    __hash__ = None

    METRIC_STANDARD_THREAD = 0
    METRIC_FINE_THREAD = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ThreadTypes.__setattr__ = __enum_setattr
ThreadTypes.__delattr__ = __enum_delattr
