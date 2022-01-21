'''_5008.py

ConnectionCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4855
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7256
from mastapy._internal.python_net import python_net_import

_CONNECTION_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'ConnectionCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionCompoundModalAnalysis',)


class ConnectionCompoundModalAnalysis(_7256.ConnectionCompoundAnalysis):
    '''ConnectionCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4855.ConnectionModalAnalysis]':
        '''List[ConnectionModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4855.ConnectionModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4855.ConnectionModalAnalysis]':
        '''List[ConnectionModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4855.ConnectionModalAnalysis))
        return value
