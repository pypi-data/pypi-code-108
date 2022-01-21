'''_6526.py

AdvancedTimeSteppingAnalysisForModulationStaticLoadCase
'''


from mastapy.system_model.analyses_and_results.static_loads import _6519
from mastapy._internal.python_net import python_net_import

_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_STATIC_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'AdvancedTimeSteppingAnalysisForModulationStaticLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedTimeSteppingAnalysisForModulationStaticLoadCase',)


class AdvancedTimeSteppingAnalysisForModulationStaticLoadCase(_6519.StaticLoadCase):
    '''AdvancedTimeSteppingAnalysisForModulationStaticLoadCase

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_STATIC_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedTimeSteppingAnalysisForModulationStaticLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
