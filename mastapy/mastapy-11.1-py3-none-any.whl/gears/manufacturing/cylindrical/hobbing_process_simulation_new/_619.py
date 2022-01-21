'''_619.py

AnalysisMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ANALYSIS_METHOD = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'AnalysisMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('AnalysisMethod',)


class AnalysisMethod(Enum):
    '''AnalysisMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ANALYSIS_METHOD

    __hash__ = None

    NEWTON_RAPHSON = 0
    HEURISTIC_SEARCH = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AnalysisMethod.__setattr__ = __enum_setattr
AnalysisMethod.__delattr__ = __enum_delattr
