'''_6156.py

ConicalGearMeshCompoundDynamicAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6026
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6182
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'ConicalGearMeshCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundDynamicAnalysis',)


class ConicalGearMeshCompoundDynamicAnalysis(_6182.GearMeshCompoundDynamicAnalysis):
    '''ConicalGearMeshCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundDynamicAnalysis]':
        '''List[ConicalGearMeshCompoundDynamicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_6026.ConicalGearMeshDynamicAnalysis]':
        '''List[ConicalGearMeshDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6026.ConicalGearMeshDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6026.ConicalGearMeshDynamicAnalysis]':
        '''List[ConicalGearMeshDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6026.ConicalGearMeshDynamicAnalysis))
        return value
