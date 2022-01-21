'''_6863.py

AGMAGleasonConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6732
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6891
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'AGMAGleasonConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation',)


class AGMAGleasonConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation(_6891.ConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''AGMAGleasonConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6732.AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation]':
        '''List[AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6732.AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6732.AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation]':
        '''List[AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6732.AGMAGleasonConicalGearMeshAdvancedTimeSteppingAnalysisForModulation))
        return value
