'''_3742.py

StraightBevelSunGearCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3613
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3735
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_SUN_GEAR_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'StraightBevelSunGearCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelSunGearCompoundStabilityAnalysis',)


class StraightBevelSunGearCompoundStabilityAnalysis(_3735.StraightBevelDiffGearCompoundStabilityAnalysis):
    '''StraightBevelSunGearCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_SUN_GEAR_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelSunGearCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_3613.StraightBevelSunGearStabilityAnalysis]':
        '''List[StraightBevelSunGearStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3613.StraightBevelSunGearStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3613.StraightBevelSunGearStabilityAnalysis]':
        '''List[StraightBevelSunGearStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3613.StraightBevelSunGearStabilityAnalysis))
        return value
