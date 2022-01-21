'''_6192.py

KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2278
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6063
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6189
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis',)


class KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis(_6189.KlingelnbergCycloPalloidConicalGearCompoundDynamicAnalysis):
    '''KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2278.KlingelnbergCycloPalloidHypoidGear':
        '''KlingelnbergCycloPalloidHypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2278.KlingelnbergCycloPalloidHypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6063.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6063.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6063.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis]':
        '''List[KlingelnbergCycloPalloidHypoidGearDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6063.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis))
        return value
