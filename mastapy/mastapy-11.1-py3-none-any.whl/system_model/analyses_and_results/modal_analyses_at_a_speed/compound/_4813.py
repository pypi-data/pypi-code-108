'''_4813.py

VirtualComponentCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4684
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4768
from mastapy._internal.python_net import python_net_import

_VIRTUAL_COMPONENT_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'VirtualComponentCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualComponentCompoundModalAnalysisAtASpeed',)


class VirtualComponentCompoundModalAnalysisAtASpeed(_4768.MountableComponentCompoundModalAnalysisAtASpeed):
    '''VirtualComponentCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_COMPONENT_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualComponentCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4684.VirtualComponentModalAnalysisAtASpeed]':
        '''List[VirtualComponentModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4684.VirtualComponentModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4684.VirtualComponentModalAnalysisAtASpeed]':
        '''List[VirtualComponentModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4684.VirtualComponentModalAnalysisAtASpeed))
        return value
