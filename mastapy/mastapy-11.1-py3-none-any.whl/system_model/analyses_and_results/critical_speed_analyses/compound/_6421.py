'''_6421.py

ConicalGearCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6290
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6447
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'ConicalGearCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundCriticalSpeedAnalysis',)


class ConicalGearCompoundCriticalSpeedAnalysis(_6447.GearCompoundCriticalSpeedAnalysis):
    '''ConicalGearCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundCriticalSpeedAnalysis]':
        '''List[ConicalGearCompoundCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6290.ConicalGearCriticalSpeedAnalysis]':
        '''List[ConicalGearCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6290.ConicalGearCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6290.ConicalGearCriticalSpeedAnalysis]':
        '''List[ConicalGearCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6290.ConicalGearCriticalSpeedAnalysis))
        return value
