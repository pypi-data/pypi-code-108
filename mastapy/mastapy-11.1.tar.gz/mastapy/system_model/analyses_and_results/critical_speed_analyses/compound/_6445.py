'''_6445.py

FEPartCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6316
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6391
from mastapy._internal.python_net import python_net_import

_FE_PART_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'FEPartCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartCompoundCriticalSpeedAnalysis',)


class FEPartCompoundCriticalSpeedAnalysis(_6391.AbstractShaftOrHousingCompoundCriticalSpeedAnalysis):
    '''FEPartCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _FE_PART_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6316.FEPartCriticalSpeedAnalysis]':
        '''List[FEPartCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6316.FEPartCriticalSpeedAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[FEPartCompoundCriticalSpeedAnalysis]':
        '''List[FEPartCompoundCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartCompoundCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6316.FEPartCriticalSpeedAnalysis]':
        '''List[FEPartCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6316.FEPartCriticalSpeedAnalysis))
        return value
