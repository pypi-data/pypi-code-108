'''_2152.py

ThermalExpansionOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_THERMAL_EXPANSION_OPTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'ThermalExpansionOption')


__docformat__ = 'restructuredtext en'
__all__ = ('ThermalExpansionOption',)


class ThermalExpansionOption(Enum):
    '''ThermalExpansionOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _THERMAL_EXPANSION_OPTION

    __hash__ = None

    UNIFORM = 0
    SPECIFIED_FORCE = 1
    SPECIFIED_DISPLACEMENT = 2
    CALCULATED_USING_MATERIAL_PROPERTIES = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ThermalExpansionOption.__setattr__ = __enum_setattr
ThermalExpansionOption.__delattr__ = __enum_delattr
