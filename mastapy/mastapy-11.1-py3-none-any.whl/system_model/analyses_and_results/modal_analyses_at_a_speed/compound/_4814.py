'''_4814.py

WormGearCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.part_model.gears import _2291
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4686
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4749
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'WormGearCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearCompoundModalAnalysisAtASpeed',)


class WormGearCompoundModalAnalysisAtASpeed(_4749.GearCompoundModalAnalysisAtASpeed):
    '''WormGearCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2291.WormGear':
        '''WormGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2291.WormGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4686.WormGearModalAnalysisAtASpeed]':
        '''List[WormGearModalAnalysisAtASpeed]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4686.WormGearModalAnalysisAtASpeed))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4686.WormGearModalAnalysisAtASpeed]':
        '''List[WormGearModalAnalysisAtASpeed]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4686.WormGearModalAnalysisAtASpeed))
        return value
