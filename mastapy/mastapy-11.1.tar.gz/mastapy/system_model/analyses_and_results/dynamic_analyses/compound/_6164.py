'''_6164.py

CVTCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6034
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6133
from mastapy._internal.python_net import python_net_import

_CVT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CVTCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTCompoundDynamicAnalysis',)


class CVTCompoundDynamicAnalysis(_6133.BeltDriveCompoundDynamicAnalysis):
    '''CVTCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6034.CVTDynamicAnalysis]':
        '''List[CVTDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6034.CVTDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6034.CVTDynamicAnalysis]':
        '''List[CVTDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6034.CVTDynamicAnalysis))
        return value
