'''_6412.py

ClutchHalfCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6281
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6428
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'ClutchHalfCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalfCompoundCriticalSpeedAnalysis',)


class ClutchHalfCompoundCriticalSpeedAnalysis(_6428.CouplingHalfCompoundCriticalSpeedAnalysis):
    '''ClutchHalfCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalfCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2319.ClutchHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6281.ClutchHalfCriticalSpeedAnalysis]':
        '''List[ClutchHalfCriticalSpeedAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6281.ClutchHalfCriticalSpeedAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6281.ClutchHalfCriticalSpeedAnalysis]':
        '''List[ClutchHalfCriticalSpeedAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6281.ClutchHalfCriticalSpeedAnalysis))
        return value
