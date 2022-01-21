'''_3727.py

ShaftToMountableComponentConnectionCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3596
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3633
from mastapy._internal.python_net import python_net_import

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ShaftToMountableComponentConnectionCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftToMountableComponentConnectionCompoundStabilityAnalysis',)


class ShaftToMountableComponentConnectionCompoundStabilityAnalysis(_3633.AbstractShaftToMountableComponentConnectionCompoundStabilityAnalysis):
    '''ShaftToMountableComponentConnectionCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftToMountableComponentConnectionCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3596.ShaftToMountableComponentConnectionStabilityAnalysis]':
        '''List[ShaftToMountableComponentConnectionStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3596.ShaftToMountableComponentConnectionStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3596.ShaftToMountableComponentConnectionStabilityAnalysis]':
        '''List[ShaftToMountableComponentConnectionStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3596.ShaftToMountableComponentConnectionStabilityAnalysis))
        return value
