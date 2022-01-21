'''_6448.py

GearMeshCompoundCriticalSpeedAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.critical_speed_analyses.compound import _6454
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound', 'GearMeshCompoundCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundCriticalSpeedAnalysis',)


class GearMeshCompoundCriticalSpeedAnalysis(_6454.InterMountableComponentConnectionCompoundCriticalSpeedAnalysis):
    '''GearMeshCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6319.GearMeshCriticalSpeedAnalysis]':
        '''List[GearMeshCriticalSpeedAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6319.GearMeshCriticalSpeedAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6319.GearMeshCriticalSpeedAnalysis]':
        '''List[GearMeshCriticalSpeedAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6319.GearMeshCriticalSpeedAnalysis))
        return value
