'''_3692.py

HypoidGearCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2274
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3563
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3634
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'HypoidGearCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearCompoundStabilityAnalysis',)


class HypoidGearCompoundStabilityAnalysis(_3634.AGMAGleasonConicalGearCompoundStabilityAnalysis):
    '''HypoidGearCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2274.HypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3563.HypoidGearStabilityAnalysis]':
        '''List[HypoidGearStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3563.HypoidGearStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3563.HypoidGearStabilityAnalysis]':
        '''List[HypoidGearStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3563.HypoidGearStabilityAnalysis))
        return value
