'''_6503.py

SynchroniserHalfCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2344
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6374
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6504
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_HALF_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'SynchroniserHalfCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserHalfCompoundCriticalSpeedAnalysis',)


class SynchroniserHalfCompoundCriticalSpeedAnalysis(_6504.SynchroniserPartCompoundCriticalSpeedAnalysis):
    '''SynchroniserHalfCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_HALF_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserHalfCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2344.SynchroniserHalf':
        '''SynchroniserHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2344.SynchroniserHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6374.SynchroniserHalfCriticalSpeedAnalysis]':
        '''List[SynchroniserHalfCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6374.SynchroniserHalfCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6374.SynchroniserHalfCriticalSpeedAnalysis]':
        '''List[SynchroniserHalfCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6374.SynchroniserHalfCriticalSpeedAnalysis))
        return value
