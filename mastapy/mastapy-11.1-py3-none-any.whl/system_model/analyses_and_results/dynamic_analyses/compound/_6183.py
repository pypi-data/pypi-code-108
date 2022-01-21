'''_6183.py

GearSetCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6054
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6221
from mastapy._internal.python_net import python_net_import

_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'GearSetCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetCompoundDynamicAnalysis',)


class GearSetCompoundDynamicAnalysis(_6221.SpecialisedAssemblyCompoundDynamicAnalysis):
    '''GearSetCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_6054.GearSetDynamicAnalysis]':
        '''List[GearSetDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6054.GearSetDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6054.GearSetDynamicAnalysis]':
        '''List[GearSetDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6054.GearSetDynamicAnalysis))
        return value
