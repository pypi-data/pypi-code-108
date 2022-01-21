'''_6160.py

CouplingCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6031
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6221
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CouplingCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundDynamicAnalysis',)


class CouplingCompoundDynamicAnalysis(_6221.SpecialisedAssemblyCompoundDynamicAnalysis):
    '''CouplingCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_6031.CouplingDynamicAnalysis]':
        '''List[CouplingDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6031.CouplingDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6031.CouplingDynamicAnalysis]':
        '''List[CouplingDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6031.CouplingDynamicAnalysis))
        return value
