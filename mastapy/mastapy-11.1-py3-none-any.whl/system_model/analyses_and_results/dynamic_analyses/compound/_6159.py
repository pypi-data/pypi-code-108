'''_6159.py

ConnectorCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6029
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6200
from mastapy._internal.python_net import python_net_import

_CONNECTOR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'ConnectorCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorCompoundDynamicAnalysis',)


class ConnectorCompoundDynamicAnalysis(_6200.MountableComponentCompoundDynamicAnalysis):
    '''ConnectorCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_6029.ConnectorDynamicAnalysis]':
        '''List[ConnectorDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6029.ConnectorDynamicAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_6029.ConnectorDynamicAnalysis]':
        '''List[ConnectorDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6029.ConnectorDynamicAnalysis))
        return value
