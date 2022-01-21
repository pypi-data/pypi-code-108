'''_5060.py

PowerLoadCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2213
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4913
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5095
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'PowerLoadCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadCompoundModalAnalysis',)


class PowerLoadCompoundModalAnalysis(_5095.VirtualComponentCompoundModalAnalysis):
    '''PowerLoadCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4913.PowerLoadModalAnalysis]':
        '''List[PowerLoadModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4913.PowerLoadModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4913.PowerLoadModalAnalysis]':
        '''List[PowerLoadModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4913.PowerLoadModalAnalysis))
        return value
