'''_6393.py

AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6262
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6421
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis',)


class AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis(_6421.ConicalGearCompoundCriticalSpeedAnalysis):
    '''AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6262.AGMAGleasonConicalGearCriticalSpeedAnalysis]':
        '''List[AGMAGleasonConicalGearCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6262.AGMAGleasonConicalGearCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6262.AGMAGleasonConicalGearCriticalSpeedAnalysis]':
        '''List[AGMAGleasonConicalGearCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6262.AGMAGleasonConicalGearCriticalSpeedAnalysis))
        return value
