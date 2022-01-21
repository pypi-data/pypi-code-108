'''_6481.py

RollingRingCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2336
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6353
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6428
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'RollingRingCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingCompoundCriticalSpeedAnalysis',)


class RollingRingCompoundCriticalSpeedAnalysis(_6428.CouplingHalfCompoundCriticalSpeedAnalysis):
    '''RollingRingCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2336.RollingRing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6353.RollingRingCriticalSpeedAnalysis]':
        '''List[RollingRingCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6353.RollingRingCriticalSpeedAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[RollingRingCompoundCriticalSpeedAnalysis]':
        '''List[RollingRingCompoundCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingCompoundCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6353.RollingRingCriticalSpeedAnalysis]':
        '''List[RollingRingCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6353.RollingRingCriticalSpeedAnalysis))
        return value
