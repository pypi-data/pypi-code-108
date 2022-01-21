'''_4776.py

PlanetCarrierCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model import _2210
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4647
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4768
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'PlanetCarrierCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierCompoundModalAnalysisAtASpeed',)


class PlanetCarrierCompoundModalAnalysisAtASpeed(_4768.MountableComponentCompoundModalAnalysisAtASpeed):
    '''PlanetCarrierCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2210.PlanetCarrier)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4647.PlanetCarrierModalAnalysisAtASpeed]':
        '''List[PlanetCarrierModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4647.PlanetCarrierModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4647.PlanetCarrierModalAnalysisAtASpeed]':
        '''List[PlanetCarrierModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4647.PlanetCarrierModalAnalysisAtASpeed))
        return value
