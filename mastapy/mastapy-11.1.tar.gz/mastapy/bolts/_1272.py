'''_1272.py

BoltTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BOLT_TYPES = python_net_import('SMT.MastaAPI.Bolts', 'BoltTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltTypes',)


class BoltTypes(Enum):
    '''BoltTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BOLT_TYPES

    __hash__ = None

    THROUGH_BOLTED_JOINT = 0
    TAPPED_THREAD_JOINT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BoltTypes.__setattr__ = __enum_setattr
BoltTypes.__delattr__ = __enum_delattr
