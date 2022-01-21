'''_6182.py

GearMeshCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6053
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6188
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'GearMeshCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundDynamicAnalysis',)


class GearMeshCompoundDynamicAnalysis(_6188.InterMountableComponentConnectionCompoundDynamicAnalysis):
    '''GearMeshCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6053.GearMeshDynamicAnalysis]':
        '''List[GearMeshDynamicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6053.GearMeshDynamicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6053.GearMeshDynamicAnalysis]':
        '''List[GearMeshDynamicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6053.GearMeshDynamicAnalysis))
        return value
