'''_2409.py

CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_HARMONIC_ANALYSIS_FOR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation',)


class CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation(_2359.CompoundAnalysis):
    '''CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_HARMONIC_ANALYSIS_FOR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
