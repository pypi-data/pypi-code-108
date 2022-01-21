'''_3725.py

ShaftCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3595
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3631
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ShaftCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundStabilityAnalysis',)


class ShaftCompoundStabilityAnalysis(_3631.AbstractShaftCompoundStabilityAnalysis):
    '''ShaftCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3595.ShaftStabilityAnalysis]':
        '''List[ShaftStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3595.ShaftStabilityAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundStabilityAnalysis]':
        '''List[ShaftCompoundStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3595.ShaftStabilityAnalysis]':
        '''List[ShaftStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3595.ShaftStabilityAnalysis))
        return value
