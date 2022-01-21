'''_6434.py

CycloidalDiscCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2309
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6305
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6390
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'CycloidalDiscCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCompoundCriticalSpeedAnalysis',)


class CycloidalDiscCompoundCriticalSpeedAnalysis(_6390.AbstractShaftCompoundCriticalSpeedAnalysis):
    '''CycloidalDiscCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2309.CycloidalDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6305.CycloidalDiscCriticalSpeedAnalysis]':
        '''List[CycloidalDiscCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6305.CycloidalDiscCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6305.CycloidalDiscCriticalSpeedAnalysis]':
        '''List[CycloidalDiscCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6305.CycloidalDiscCriticalSpeedAnalysis))
        return value
