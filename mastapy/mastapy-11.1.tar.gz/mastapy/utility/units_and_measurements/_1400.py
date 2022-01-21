'''_1400.py

MeasurementSystem
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MEASUREMENT_SYSTEM = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements', 'MeasurementSystem')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementSystem',)


class MeasurementSystem(Enum):
    '''MeasurementSystem

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MEASUREMENT_SYSTEM

    __hash__ = None

    METRIC = 0
    IMPERIAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MeasurementSystem.__setattr__ = __enum_setattr
MeasurementSystem.__delattr__ = __enum_delattr
