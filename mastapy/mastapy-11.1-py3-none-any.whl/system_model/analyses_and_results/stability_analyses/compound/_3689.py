'''_3689.py

GearMeshCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3557
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3695
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'GearMeshCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundStabilityAnalysis',)


class GearMeshCompoundStabilityAnalysis(_3695.InterMountableComponentConnectionCompoundStabilityAnalysis):
    '''GearMeshCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3557.GearMeshStabilityAnalysis]':
        '''List[GearMeshStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3557.GearMeshStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3557.GearMeshStabilityAnalysis]':
        '''List[GearMeshStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3557.GearMeshStabilityAnalysis))
        return value
