'''_3964.py

KlingelnbergCycloPalloidConicalGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.power_flows import _3833
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows.compound import _3930
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'KlingelnbergCycloPalloidConicalGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearCompoundPowerFlow',)


class KlingelnbergCycloPalloidConicalGearCompoundPowerFlow(_3930.ConicalGearCompoundPowerFlow):
    '''KlingelnbergCycloPalloidConicalGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_3833.KlingelnbergCycloPalloidConicalGearPowerFlow]':
        '''List[KlingelnbergCycloPalloidConicalGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3833.KlingelnbergCycloPalloidConicalGearPowerFlow))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_3833.KlingelnbergCycloPalloidConicalGearPowerFlow]':
        '''List[KlingelnbergCycloPalloidConicalGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3833.KlingelnbergCycloPalloidConicalGearPowerFlow))
        return value
