'''_4750.py

GearMeshCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4620
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4756
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'GearMeshCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundModalAnalysisAtASpeed',)


class GearMeshCompoundModalAnalysisAtASpeed(_4756.InterMountableComponentConnectionCompoundModalAnalysisAtASpeed):
    '''GearMeshCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4620.GearMeshModalAnalysisAtASpeed]':
        '''List[GearMeshModalAnalysisAtASpeed]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4620.GearMeshModalAnalysisAtASpeed))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4620.GearMeshModalAnalysisAtASpeed]':
        '''List[GearMeshModalAnalysisAtASpeed]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4620.GearMeshModalAnalysisAtASpeed))
        return value
