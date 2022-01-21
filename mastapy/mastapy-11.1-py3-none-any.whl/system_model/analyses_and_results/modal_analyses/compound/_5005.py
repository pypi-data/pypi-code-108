'''_5005.py

ConicalGearCompoundModalAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4853
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5031
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'ConicalGearCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundModalAnalysis',)


class ConicalGearCompoundModalAnalysis(_5031.GearCompoundModalAnalysis):
    '''ConicalGearCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundModalAnalysis]':
        '''List[ConicalGearCompoundModalAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4853.ConicalGearModalAnalysis]':
        '''List[ConicalGearModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4853.ConicalGearModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4853.ConicalGearModalAnalysis]':
        '''List[ConicalGearModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4853.ConicalGearModalAnalysis))
        return value
