'''_5010.py

CouplingCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4860
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5071
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'CouplingCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundModalAnalysis',)


class CouplingCompoundModalAnalysis(_5071.SpecialisedAssemblyCompoundModalAnalysis):
    '''CouplingCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4860.CouplingModalAnalysis]':
        '''List[CouplingModalAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4860.CouplingModalAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4860.CouplingModalAnalysis]':
        '''List[CouplingModalAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4860.CouplingModalAnalysis))
        return value
