'''_3647.py

BevelGearMeshCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3514
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3635
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'BevelGearMeshCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMeshCompoundStabilityAnalysis',)


class BevelGearMeshCompoundStabilityAnalysis(_3635.AGMAGleasonConicalGearMeshCompoundStabilityAnalysis):
    '''BevelGearMeshCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMeshCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3514.BevelGearMeshStabilityAnalysis]':
        '''List[BevelGearMeshStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3514.BevelGearMeshStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3514.BevelGearMeshStabilityAnalysis]':
        '''List[BevelGearMeshStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3514.BevelGearMeshStabilityAnalysis))
        return value
