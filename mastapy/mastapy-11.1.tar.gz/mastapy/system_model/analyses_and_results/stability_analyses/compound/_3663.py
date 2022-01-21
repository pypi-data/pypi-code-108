'''_3663.py

ConicalGearMeshCompoundStabilityAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3530
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3689
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'ConicalGearMeshCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundStabilityAnalysis',)


class ConicalGearMeshCompoundStabilityAnalysis(_3689.GearMeshCompoundStabilityAnalysis):
    '''ConicalGearMeshCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundStabilityAnalysis]':
        '''List[ConicalGearMeshCompoundStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3530.ConicalGearMeshStabilityAnalysis]':
        '''List[ConicalGearMeshStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3530.ConicalGearMeshStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3530.ConicalGearMeshStabilityAnalysis]':
        '''List[ConicalGearMeshStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3530.ConicalGearMeshStabilityAnalysis))
        return value
