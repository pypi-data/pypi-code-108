'''_4021.py

WormGearCompoundPowerFlow
'''


from typing import List

from mastapy.gears.rating.worm import _338
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.gears import _2291
from mastapy.system_model.analyses_and_results.power_flows import _3893
from mastapy.system_model.analyses_and_results.power_flows.compound import _3956
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'WormGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearCompoundPowerFlow',)


class WormGearCompoundPowerFlow(_3956.GearCompoundPowerFlow):
    '''WormGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_duty_cycle_rating(self) -> '_338.WormGearDutyCycleRating':
        '''WormGearDutyCycleRating: 'GearDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_338.WormGearDutyCycleRating)(self.wrapped.GearDutyCycleRating) if self.wrapped.GearDutyCycleRating is not None else None

    @property
    def worm_gear_duty_cycle_rating(self) -> '_338.WormGearDutyCycleRating':
        '''WormGearDutyCycleRating: 'WormGearDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_338.WormGearDutyCycleRating)(self.wrapped.WormGearDutyCycleRating) if self.wrapped.WormGearDutyCycleRating is not None else None

    @property
    def component_design(self) -> '_2291.WormGear':
        '''WormGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2291.WormGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3893.WormGearPowerFlow]':
        '''List[WormGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3893.WormGearPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3893.WormGearPowerFlow]':
        '''List[WormGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3893.WormGearPowerFlow))
        return value
