'''_3649.py

BoltCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2184
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3518
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3655
from mastapy._internal.python_net import python_net_import

_BOLT_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'BoltCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltCompoundStabilityAnalysis',)


class BoltCompoundStabilityAnalysis(_3655.ComponentCompoundStabilityAnalysis):
    '''BoltCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _BOLT_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2184.Bolt':
        '''Bolt: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2184.Bolt)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3518.BoltStabilityAnalysis]':
        '''List[BoltStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3518.BoltStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3518.BoltStabilityAnalysis]':
        '''List[BoltStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3518.BoltStabilityAnalysis))
        return value
