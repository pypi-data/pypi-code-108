'''_6729.py

AtsamNaturalFrequencyViewOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ATSAM_NATURAL_FREQUENCY_VIEW_OPTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'AtsamNaturalFrequencyViewOption')


__docformat__ = 'restructuredtext en'
__all__ = ('AtsamNaturalFrequencyViewOption',)


class AtsamNaturalFrequencyViewOption(Enum):
    '''AtsamNaturalFrequencyViewOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ATSAM_NATURAL_FREQUENCY_VIEW_OPTION

    __hash__ = None

    ALL_MODES_AT_SELECTED_LARGE_TIME_STEP = 0
    RANGE_OF_SELECTED_MODE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AtsamNaturalFrequencyViewOption.__setattr__ = __enum_setattr
AtsamNaturalFrequencyViewOption.__delattr__ = __enum_delattr
