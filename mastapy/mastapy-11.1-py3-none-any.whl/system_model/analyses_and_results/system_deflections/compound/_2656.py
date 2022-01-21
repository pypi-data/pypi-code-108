'''_2656.py

KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2278
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2508
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2653
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection',)


class KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection(_2653.KlingelnbergCycloPalloidConicalGearCompoundSystemDeflection):
    '''KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_2508.KlingelnbergCycloPalloidHypoidGearSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2508.KlingelnbergCycloPalloidHypoidGearSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2508.KlingelnbergCycloPalloidHypoidGearSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2508.KlingelnbergCycloPalloidHypoidGearSystemDeflection))
        return value
