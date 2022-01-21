'''_5014.py

CVTCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4862
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4983
from mastapy._internal.python_net import python_net_import

_CVT_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'CVTCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTCompoundModalAnalysis',)


class CVTCompoundModalAnalysis(_4983.BeltDriveCompoundModalAnalysis):
    '''CVTCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4862.CVTModalAnalysis]':
        '''List[CVTModalAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4862.CVTModalAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4862.CVTModalAnalysis]':
        '''List[CVTModalAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4862.CVTModalAnalysis))
        return value
