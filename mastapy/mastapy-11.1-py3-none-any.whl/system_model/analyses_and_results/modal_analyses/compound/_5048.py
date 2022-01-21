'''_5048.py

MassDiscCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4897
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5095
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'MassDiscCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundModalAnalysis',)


class MassDiscCompoundModalAnalysis(_5095.VirtualComponentCompoundModalAnalysis):
    '''MassDiscCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4897.MassDiscModalAnalysis]':
        '''List[MassDiscModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4897.MassDiscModalAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundModalAnalysis]':
        '''List[MassDiscCompoundModalAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4897.MassDiscModalAnalysis]':
        '''List[MassDiscModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4897.MassDiscModalAnalysis))
        return value
