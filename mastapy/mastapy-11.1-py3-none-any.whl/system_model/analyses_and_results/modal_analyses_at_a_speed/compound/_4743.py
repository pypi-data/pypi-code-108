'''_4743.py

ExternalCADModelCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2193
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4614
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4716
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'ExternalCADModelCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModelCompoundModalAnalysisAtASpeed',)


class ExternalCADModelCompoundModalAnalysisAtASpeed(_4716.ComponentCompoundModalAnalysisAtASpeed):
    '''ExternalCADModelCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModelCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2193.ExternalCADModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4614.ExternalCADModelModalAnalysisAtASpeed]':
        '''List[ExternalCADModelModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4614.ExternalCADModelModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4614.ExternalCADModelModalAnalysisAtASpeed]':
        '''List[ExternalCADModelModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4614.ExternalCADModelModalAnalysisAtASpeed))
        return value
