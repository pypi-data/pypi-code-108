'''_3756.py

ZerolBevelGearCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2293
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3629
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3646
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ZerolBevelGearCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearCompoundStabilityAnalysis',)


class ZerolBevelGearCompoundStabilityAnalysis(_3646.BevelGearCompoundStabilityAnalysis):
    '''ZerolBevelGearCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2293.ZerolBevelGear':
        '''ZerolBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2293.ZerolBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3629.ZerolBevelGearStabilityAnalysis]':
        '''List[ZerolBevelGearStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3629.ZerolBevelGearStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3629.ZerolBevelGearStabilityAnalysis]':
        '''List[ZerolBevelGearStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3629.ZerolBevelGearStabilityAnalysis))
        return value
