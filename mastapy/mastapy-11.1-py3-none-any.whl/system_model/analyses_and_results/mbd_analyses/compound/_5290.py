'''_5290.py

ConnectorCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.mbd_analyses import _5141
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5331
from mastapy._internal.python_net import python_net_import

_CONNECTOR_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'ConnectorCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorCompoundMultibodyDynamicsAnalysis',)


class ConnectorCompoundMultibodyDynamicsAnalysis(_5331.MountableComponentCompoundMultibodyDynamicsAnalysis):
    '''ConnectorCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5141.ConnectorMultibodyDynamicsAnalysis]':
        '''List[ConnectorMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5141.ConnectorMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5141.ConnectorMultibodyDynamicsAnalysis]':
        '''List[ConnectorMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5141.ConnectorMultibodyDynamicsAnalysis))
        return value
