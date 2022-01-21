'''_3717.py

PowerLoadCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2213
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3586
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3752
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'PowerLoadCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadCompoundStabilityAnalysis',)


class PowerLoadCompoundStabilityAnalysis(_3752.VirtualComponentCompoundStabilityAnalysis):
    '''PowerLoadCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3586.PowerLoadStabilityAnalysis]':
        '''List[PowerLoadStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3586.PowerLoadStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3586.PowerLoadStabilityAnalysis]':
        '''List[PowerLoadStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3586.PowerLoadStabilityAnalysis))
        return value
