'''_5291.py

CouplingCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.mbd_analyses import _5144
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5352
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'CouplingCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundMultibodyDynamicsAnalysis',)


class CouplingCompoundMultibodyDynamicsAnalysis(_5352.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis):
    '''CouplingCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_5144.CouplingMultibodyDynamicsAnalysis]':
        '''List[CouplingMultibodyDynamicsAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5144.CouplingMultibodyDynamicsAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5144.CouplingMultibodyDynamicsAnalysis]':
        '''List[CouplingMultibodyDynamicsAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5144.CouplingMultibodyDynamicsAnalysis))
        return value
