'''_5033.py

GearSetCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4882
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5071
from mastapy._internal.python_net import python_net_import

_GEAR_SET_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'GearSetCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetCompoundModalAnalysis',)


class GearSetCompoundModalAnalysis(_5071.SpecialisedAssemblyCompoundModalAnalysis):
    '''GearSetCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4882.GearSetModalAnalysis]':
        '''List[GearSetModalAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4882.GearSetModalAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4882.GearSetModalAnalysis]':
        '''List[GearSetModalAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4882.GearSetModalAnalysis))
        return value
