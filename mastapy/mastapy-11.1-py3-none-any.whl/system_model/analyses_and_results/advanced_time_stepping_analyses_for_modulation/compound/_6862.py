'''_6862.py

AGMAGleasonConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6731
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6890
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'AGMAGleasonConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation',)


class AGMAGleasonConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation(_6890.ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''AGMAGleasonConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6731.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6731.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6731.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6731.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation))
        return value
