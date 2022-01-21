'''_5067.py

RootAssemblyCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4920
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4980
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'RootAssemblyCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyCompoundModalAnalysis',)


class RootAssemblyCompoundModalAnalysis(_4980.AssemblyCompoundModalAnalysis):
    '''RootAssemblyCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4920.RootAssemblyModalAnalysis]':
        '''List[RootAssemblyModalAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4920.RootAssemblyModalAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4920.RootAssemblyModalAnalysis]':
        '''List[RootAssemblyModalAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4920.RootAssemblyModalAnalysis))
        return value
