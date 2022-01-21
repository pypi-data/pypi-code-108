'''_5011.py

CouplingConnectionCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4858
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5038
from mastapy._internal.python_net import python_net_import

_COUPLING_CONNECTION_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'CouplingConnectionCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingConnectionCompoundModalAnalysis',)


class CouplingConnectionCompoundModalAnalysis(_5038.InterMountableComponentConnectionCompoundModalAnalysis):
    '''CouplingConnectionCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _COUPLING_CONNECTION_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingConnectionCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4858.CouplingConnectionModalAnalysis]':
        '''List[CouplingConnectionModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4858.CouplingConnectionModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4858.CouplingConnectionModalAnalysis]':
        '''List[CouplingConnectionModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4858.CouplingConnectionModalAnalysis))
        return value
