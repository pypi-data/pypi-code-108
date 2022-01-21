'''_1036.py

TolerancedMetalMeasurements
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TOLERANCED_METAL_MEASUREMENTS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'TolerancedMetalMeasurements')


__docformat__ = 'restructuredtext en'
__all__ = ('TolerancedMetalMeasurements',)


class TolerancedMetalMeasurements(Enum):
    '''TolerancedMetalMeasurements

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TOLERANCED_METAL_MEASUREMENTS

    __hash__ = None

    MINIMUM_THICKNESS = 0
    AVERAGE_THICKNESS = 1
    MAXIMUM_THICKNESS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TolerancedMetalMeasurements.__setattr__ = __enum_setattr
TolerancedMetalMeasurements.__delattr__ = __enum_delattr
