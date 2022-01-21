'''_6191.py

KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.dynamic_analyses import _6062
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6157
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis',)


class KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis(_6157.ConicalGearSetCompoundDynamicAnalysis):
    '''KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_6062.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6062.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6062.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6062.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis))
        return value
