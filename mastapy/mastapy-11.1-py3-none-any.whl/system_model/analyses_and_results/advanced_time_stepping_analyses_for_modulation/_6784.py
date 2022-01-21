'''_6784.py

FEPartAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5745
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5833
from mastapy.system_model.part_model import _2194
from mastapy.system_model.analyses_and_results.static_loads import _6602
from mastapy.system_model.analyses_and_results.system_deflections import _2492
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6726
from mastapy._internal.python_net import python_net_import

_FE_PART_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'FEPartAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartAdvancedTimeSteppingAnalysisForModulation',)


class FEPartAdvancedTimeSteppingAnalysisForModulation(_6726.AbstractShaftOrHousingAdvancedTimeSteppingAnalysisForModulation):
    '''FEPartAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _FE_PART_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def export(self) -> '_5745.HarmonicAnalysisFEExportOptions':
        '''HarmonicAnalysisFEExportOptions: 'Export' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5745.HarmonicAnalysisFEExportOptions)(self.wrapped.Export) if self.wrapped.Export is not None else None

    @property
    def results(self) -> '_5833.FEPartHarmonicAnalysisResultsPropertyAccessor':
        '''FEPartHarmonicAnalysisResultsPropertyAccessor: 'Results' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5833.FEPartHarmonicAnalysisResultsPropertyAccessor)(self.wrapped.Results) if self.wrapped.Results is not None else None

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6602.FEPartLoadCase':
        '''FEPartLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6602.FEPartLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2492.FEPartSystemDeflection':
        '''FEPartSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2492.FEPartSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None

    @property
    def planetaries(self) -> 'List[FEPartAdvancedTimeSteppingAnalysisForModulation]':
        '''List[FEPartAdvancedTimeSteppingAnalysisForModulation]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartAdvancedTimeSteppingAnalysisForModulation))
        return value
