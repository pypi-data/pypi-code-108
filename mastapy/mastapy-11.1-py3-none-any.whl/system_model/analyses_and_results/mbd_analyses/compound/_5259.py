'''_5259.py

AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.mbd_analyses import _5106
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5287
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis',)


class AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis(_5287.ConicalGearMeshCompoundMultibodyDynamicsAnalysis):
    '''AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_5106.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis]':
        '''List[AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5106.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5106.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis]':
        '''List[AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5106.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis))
        return value
