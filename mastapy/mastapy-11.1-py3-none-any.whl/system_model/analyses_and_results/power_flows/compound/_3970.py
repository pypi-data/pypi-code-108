'''_3970.py

KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2280
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3839
from mastapy.system_model.analyses_and_results.power_flows.compound import _3964
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow',)


class KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow(_3964.KlingelnbergCycloPalloidConicalGearCompoundPowerFlow):
    '''KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2280.KlingelnbergCycloPalloidSpiralBevelGear':
        '''KlingelnbergCycloPalloidSpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2280.KlingelnbergCycloPalloidSpiralBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3839.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3839.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3839.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3839.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow))
        return value
