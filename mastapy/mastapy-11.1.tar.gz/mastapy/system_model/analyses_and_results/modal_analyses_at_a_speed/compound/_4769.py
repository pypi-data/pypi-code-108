'''_4769.py

OilSealCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2207
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4640
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4727
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'OilSealCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealCompoundModalAnalysisAtASpeed',)


class OilSealCompoundModalAnalysisAtASpeed(_4727.ConnectorCompoundModalAnalysisAtASpeed):
    '''OilSealCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2207.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4640.OilSealModalAnalysisAtASpeed]':
        '''List[OilSealModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4640.OilSealModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4640.OilSealModalAnalysisAtASpeed]':
        '''List[OilSealModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4640.OilSealModalAnalysisAtASpeed))
        return value
