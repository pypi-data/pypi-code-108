'''_5096.py

WormGearCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2291
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4956
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5031
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'WormGearCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearCompoundModalAnalysis',)


class WormGearCompoundModalAnalysis(_5031.GearCompoundModalAnalysis):
    '''WormGearCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearCompoundModalAnalysis.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_4956.WormGearModalAnalysis]':
        '''List[WormGearModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4956.WormGearModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4956.WormGearModalAnalysis]':
        '''List[WormGearModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4956.WormGearModalAnalysis))
        return value
