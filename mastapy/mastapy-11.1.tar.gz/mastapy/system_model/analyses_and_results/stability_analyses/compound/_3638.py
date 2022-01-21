'''_3638.py

BearingCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2182
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3506
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3666
from mastapy._internal.python_net import python_net_import

_BEARING_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'BearingCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingCompoundStabilityAnalysis',)


class BearingCompoundStabilityAnalysis(_3666.ConnectorCompoundStabilityAnalysis):
    '''BearingCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEARING_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2182.Bearing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3506.BearingStabilityAnalysis]':
        '''List[BearingStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3506.BearingStabilityAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[BearingCompoundStabilityAnalysis]':
        '''List[BearingCompoundStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(BearingCompoundStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3506.BearingStabilityAnalysis]':
        '''List[BearingStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3506.BearingStabilityAnalysis))
        return value
