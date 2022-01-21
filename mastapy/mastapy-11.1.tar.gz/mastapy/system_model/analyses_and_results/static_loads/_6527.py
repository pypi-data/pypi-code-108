'''_6527.py

AdvancedTimeSteppingAnalysisForModulationType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'AdvancedTimeSteppingAnalysisForModulationType')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedTimeSteppingAnalysisForModulationType',)


class AdvancedTimeSteppingAnalysisForModulationType(Enum):
    '''AdvancedTimeSteppingAnalysisForModulationType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_TYPE

    __hash__ = None

    QUASI_HARMONIC_ANALYSIS = 0
    SEPARATION_OF_TIMESCALES_TIME_STEPPING = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AdvancedTimeSteppingAnalysisForModulationType.__setattr__ = __enum_setattr
AdvancedTimeSteppingAnalysisForModulationType.__delattr__ = __enum_delattr
