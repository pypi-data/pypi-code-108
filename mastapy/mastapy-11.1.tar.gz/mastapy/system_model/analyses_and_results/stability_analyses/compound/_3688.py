'''_3688.py

GearCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3559
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3707
from mastapy._internal.python_net import python_net_import

_GEAR_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'GearCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearCompoundStabilityAnalysis',)


class GearCompoundStabilityAnalysis(_3707.MountableComponentCompoundStabilityAnalysis):
    '''GearCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3559.GearStabilityAnalysis]':
        '''List[GearStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3559.GearStabilityAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3559.GearStabilityAnalysis]':
        '''List[GearStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3559.GearStabilityAnalysis))
        return value
