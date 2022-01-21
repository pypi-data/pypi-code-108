'''_5002.py

ConceptGearCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2261
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4850
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5031
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'ConceptGearCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearCompoundModalAnalysis',)


class ConceptGearCompoundModalAnalysis(_5031.GearCompoundModalAnalysis):
    '''ConceptGearCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2261.ConceptGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4850.ConceptGearModalAnalysis]':
        '''List[ConceptGearModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4850.ConceptGearModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4850.ConceptGearModalAnalysis]':
        '''List[ConceptGearModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4850.ConceptGearModalAnalysis))
        return value
