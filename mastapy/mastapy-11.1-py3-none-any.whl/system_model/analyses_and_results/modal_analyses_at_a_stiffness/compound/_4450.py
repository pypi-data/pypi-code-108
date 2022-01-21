'''_4450.py

BevelGearMeshCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4438
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'BevelGearMeshCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMeshCompoundModalAnalysisAtAStiffness',)


class BevelGearMeshCompoundModalAnalysisAtAStiffness(_4438.AGMAGleasonConicalGearMeshCompoundModalAnalysisAtAStiffness):
    '''BevelGearMeshCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMeshCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4319.BevelGearMeshModalAnalysisAtAStiffness]':
        '''List[BevelGearMeshModalAnalysisAtAStiffness]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4319.BevelGearMeshModalAnalysisAtAStiffness))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4319.BevelGearMeshModalAnalysisAtAStiffness]':
        '''List[BevelGearMeshModalAnalysisAtAStiffness]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4319.BevelGearMeshModalAnalysisAtAStiffness))
        return value
