'''_6890.py

ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6760
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6916
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation',)


class ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation(_6916.GearCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6760.ConicalGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ConicalGearAdvancedTimeSteppingAnalysisForModulation]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6760.ConicalGearAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6760.ConicalGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[ConicalGearAdvancedTimeSteppingAnalysisForModulation]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6760.ConicalGearAdvancedTimeSteppingAnalysisForModulation))
        return value
