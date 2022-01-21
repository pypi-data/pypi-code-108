'''_3662.py

ConicalGearCompoundStabilityAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3532
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3688
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ConicalGearCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundStabilityAnalysis',)


class ConicalGearCompoundStabilityAnalysis(_3688.GearCompoundStabilityAnalysis):
    '''ConicalGearCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundStabilityAnalysis]':
        '''List[ConicalGearCompoundStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3532.ConicalGearStabilityAnalysis]':
        '''List[ConicalGearStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3532.ConicalGearStabilityAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3532.ConicalGearStabilityAnalysis]':
        '''List[ConicalGearStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3532.ConicalGearStabilityAnalysis))
        return value
