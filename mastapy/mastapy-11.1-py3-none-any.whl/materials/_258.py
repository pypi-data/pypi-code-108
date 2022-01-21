'''_258.py

WindTurbineStandards
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_WIND_TURBINE_STANDARDS = python_net_import('SMT.MastaAPI.Materials', 'WindTurbineStandards')


__docformat__ = 'restructuredtext en'
__all__ = ('WindTurbineStandards',)


class WindTurbineStandards(Enum):
    '''WindTurbineStandards

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _WIND_TURBINE_STANDARDS

    __hash__ = None

    NONE = 0
    GL = 1
    ISO_814004 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


WindTurbineStandards.__setattr__ = __enum_setattr
WindTurbineStandards.__delattr__ = __enum_delattr
