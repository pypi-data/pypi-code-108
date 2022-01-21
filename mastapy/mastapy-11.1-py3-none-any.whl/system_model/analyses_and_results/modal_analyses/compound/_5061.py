'''_5061.py

PulleyCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2330, _2327
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.modal_analyses import _4914
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5012
from mastapy._internal.python_net import python_net_import

_PULLEY_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'PulleyCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PulleyCompoundModalAnalysis',)


class PulleyCompoundModalAnalysis(_5012.CouplingHalfCompoundModalAnalysis):
    '''PulleyCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _PULLEY_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PulleyCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2330.Pulley':
        '''Pulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Pulley. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4914.PulleyModalAnalysis]':
        '''List[PulleyModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4914.PulleyModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4914.PulleyModalAnalysis]':
        '''List[PulleyModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4914.PulleyModalAnalysis))
        return value
