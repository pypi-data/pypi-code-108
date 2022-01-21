'''_6422.py

ConicalGearMeshCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6291
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6448
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'ConicalGearMeshCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundCriticalSpeedAnalysis',)


class ConicalGearMeshCompoundCriticalSpeedAnalysis(_6448.GearMeshCompoundCriticalSpeedAnalysis):
    '''ConicalGearMeshCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundCriticalSpeedAnalysis]':
        '''List[ConicalGearMeshCompoundCriticalSpeedAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundCriticalSpeedAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_6291.ConicalGearMeshCriticalSpeedAnalysis]':
        '''List[ConicalGearMeshCriticalSpeedAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6291.ConicalGearMeshCriticalSpeedAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6291.ConicalGearMeshCriticalSpeedAnalysis]':
        '''List[ConicalGearMeshCriticalSpeedAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6291.ConicalGearMeshCriticalSpeedAnalysis))
        return value
