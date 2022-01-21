'''_1210.py

SplineDesignTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SPLINE_DESIGN_TYPES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'SplineDesignTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('SplineDesignTypes',)


class SplineDesignTypes(Enum):
    '''SplineDesignTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SPLINE_DESIGN_TYPES

    __hash__ = None

    DIN_548012006 = 0
    ISO_4156122005 = 1
    GBT_347812008 = 2
    JIS_B_16032001 = 3
    SAE_B9211996 = 4
    CUSTOM = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SplineDesignTypes.__setattr__ = __enum_setattr
SplineDesignTypes.__delattr__ = __enum_delattr
