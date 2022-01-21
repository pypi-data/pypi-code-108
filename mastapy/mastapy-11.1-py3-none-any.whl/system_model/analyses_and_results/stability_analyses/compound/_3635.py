'''_3635.py

AGMAGleasonConicalGearMeshCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3502
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3663
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'AGMAGleasonConicalGearMeshCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundStabilityAnalysis',)


class AGMAGleasonConicalGearMeshCompoundStabilityAnalysis(_3663.ConicalGearMeshCompoundStabilityAnalysis):
    '''AGMAGleasonConicalGearMeshCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3502.AGMAGleasonConicalGearMeshStabilityAnalysis]':
        '''List[AGMAGleasonConicalGearMeshStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3502.AGMAGleasonConicalGearMeshStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3502.AGMAGleasonConicalGearMeshStabilityAnalysis]':
        '''List[AGMAGleasonConicalGearMeshStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3502.AGMAGleasonConicalGearMeshStabilityAnalysis))
        return value
