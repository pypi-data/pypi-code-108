'''_1635.py

BearingMeasurementType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_MEASUREMENT_TYPE = python_net_import('SMT.MastaAPI.Bearings', 'BearingMeasurementType')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingMeasurementType',)


class BearingMeasurementType(Enum):
    '''BearingMeasurementType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_MEASUREMENT_TYPE

    __hash__ = None

    METRIC = 0
    INCH = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingMeasurementType.__setattr__ = __enum_setattr
BearingMeasurementType.__delattr__ = __enum_delattr
