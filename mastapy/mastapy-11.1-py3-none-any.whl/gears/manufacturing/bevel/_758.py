'''_758.py

MachineTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MACHINE_TYPES = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'MachineTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('MachineTypes',)


class MachineTypes(Enum):
    '''MachineTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MACHINE_TYPES

    __hash__ = None

    CRADLE_STYLE = 0
    PHOENIX_STYLE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MachineTypes.__setattr__ = __enum_setattr
MachineTypes.__delattr__ = __enum_delattr
