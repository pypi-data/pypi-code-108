'''_5369.py

SynchroniserPartCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.mbd_analyses import _5231
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5293
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_PART_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'SynchroniserPartCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserPartCompoundMultibodyDynamicsAnalysis',)


class SynchroniserPartCompoundMultibodyDynamicsAnalysis(_5293.CouplingHalfCompoundMultibodyDynamicsAnalysis):
    '''SynchroniserPartCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_PART_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserPartCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5231.SynchroniserPartMultibodyDynamicsAnalysis]':
        '''List[SynchroniserPartMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5231.SynchroniserPartMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5231.SynchroniserPartMultibodyDynamicsAnalysis]':
        '''List[SynchroniserPartMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5231.SynchroniserPartMultibodyDynamicsAnalysis))
        return value
