'''_5109.py

AnalysisTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ANALYSIS_TYPES = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'AnalysisTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('AnalysisTypes',)


class AnalysisTypes(Enum):
    '''AnalysisTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ANALYSIS_TYPES

    __hash__ = None

    NORMAL = 0
    RUN_UPDOWN = 1
    SIMULINK = 2
    DRIVE_CYCLE = 3
    DRIVE_CYCLE_WITH_SIMULINK = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AnalysisTypes.__setattr__ = __enum_setattr
AnalysisTypes.__delattr__ = __enum_delattr
