'''_447.py

TipReliefScuffingOptions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TIP_RELIEF_SCUFFING_OPTIONS = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'TipReliefScuffingOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('TipReliefScuffingOptions',)


class TipReliefScuffingOptions(Enum):
    '''TipReliefScuffingOptions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TIP_RELIEF_SCUFFING_OPTIONS

    __hash__ = None

    CALCULATE_USING_MICRO_GEOMETRY = 0
    CALCULATE_USING_MICRO_GEOMETRY_LIMIT_TO_OPTIMAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TipReliefScuffingOptions.__setattr__ = __enum_setattr
TipReliefScuffingOptions.__delattr__ = __enum_delattr
