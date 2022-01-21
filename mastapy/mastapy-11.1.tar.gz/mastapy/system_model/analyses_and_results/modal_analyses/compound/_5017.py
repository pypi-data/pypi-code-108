'''_5017.py

CycloidalDiscCentralBearingConnectionCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4865
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4997
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'CycloidalDiscCentralBearingConnectionCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCentralBearingConnectionCompoundModalAnalysis',)


class CycloidalDiscCentralBearingConnectionCompoundModalAnalysis(_4997.CoaxialConnectionCompoundModalAnalysis):
    '''CycloidalDiscCentralBearingConnectionCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCentralBearingConnectionCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4865.CycloidalDiscCentralBearingConnectionModalAnalysis]':
        '''List[CycloidalDiscCentralBearingConnectionModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4865.CycloidalDiscCentralBearingConnectionModalAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_4865.CycloidalDiscCentralBearingConnectionModalAnalysis]':
        '''List[CycloidalDiscCentralBearingConnectionModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4865.CycloidalDiscCentralBearingConnectionModalAnalysis))
        return value
