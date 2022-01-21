'''_4812.py

UnbalancedMassCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4683
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4813
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'UnbalancedMassCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassCompoundModalAnalysisAtASpeed',)


class UnbalancedMassCompoundModalAnalysisAtASpeed(_4813.VirtualComponentCompoundModalAnalysisAtASpeed):
    '''UnbalancedMassCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4683.UnbalancedMassModalAnalysisAtASpeed]':
        '''List[UnbalancedMassModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4683.UnbalancedMassModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4683.UnbalancedMassModalAnalysisAtASpeed]':
        '''List[UnbalancedMassModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4683.UnbalancedMassModalAnalysisAtASpeed))
        return value
