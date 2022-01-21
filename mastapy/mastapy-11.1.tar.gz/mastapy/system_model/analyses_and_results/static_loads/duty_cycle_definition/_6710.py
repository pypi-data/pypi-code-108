'''_6710.py

DestinationDesignState
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DESTINATION_DESIGN_STATE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'DestinationDesignState')


__docformat__ = 'restructuredtext en'
__all__ = ('DestinationDesignState',)


class DestinationDesignState(Enum):
    '''DestinationDesignState

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DESTINATION_DESIGN_STATE

    __hash__ = None

    NAMES = 0
    GEAR_RATIO = 1
    NONE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DestinationDesignState.__setattr__ = __enum_setattr
DestinationDesignState.__delattr__ = __enum_delattr
