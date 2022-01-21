'''_1203.py

Modules
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MODULES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'Modules')


__docformat__ = 'restructuredtext en'
__all__ = ('Modules',)


class Modules(Enum):
    '''Modules

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MODULES

    __hash__ = None

    _025MM = 0
    _05MM = 1
    _06MM = 2
    _075MM = 3
    _08MM = 4
    _1MM = 5
    _125MM = 6
    _15MM = 7
    _175MM = 8
    _2MM = 9
    _25MM = 10
    _3MM = 11
    _4MM = 12
    _5MM = 13
    _6MM = 14
    _8MM = 15
    _10MM = 16


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Modules.__setattr__ = __enum_setattr
Modules.__delattr__ = __enum_delattr
