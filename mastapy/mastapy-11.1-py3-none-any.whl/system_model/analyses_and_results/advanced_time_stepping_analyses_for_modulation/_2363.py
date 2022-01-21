'''_2363.py

AdvancedTimeSteppingAnalysisForModulation
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7254
from mastapy._internal.python_net import python_net_import

_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'AdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedTimeSteppingAnalysisForModulation',)


class AdvancedTimeSteppingAnalysisForModulation(_7254.CompoundAnalysisCase):
    '''AdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
