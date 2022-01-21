'''_3674.py

CycloidalDiscCentralBearingConnectionCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3543
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3654
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'CycloidalDiscCentralBearingConnectionCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCentralBearingConnectionCompoundStabilityAnalysis',)


class CycloidalDiscCentralBearingConnectionCompoundStabilityAnalysis(_3654.CoaxialConnectionCompoundStabilityAnalysis):
    '''CycloidalDiscCentralBearingConnectionCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCentralBearingConnectionCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3543.CycloidalDiscCentralBearingConnectionStabilityAnalysis]':
        '''List[CycloidalDiscCentralBearingConnectionStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3543.CycloidalDiscCentralBearingConnectionStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3543.CycloidalDiscCentralBearingConnectionStabilityAnalysis]':
        '''List[CycloidalDiscCentralBearingConnectionStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3543.CycloidalDiscCentralBearingConnectionStabilityAnalysis))
        return value
