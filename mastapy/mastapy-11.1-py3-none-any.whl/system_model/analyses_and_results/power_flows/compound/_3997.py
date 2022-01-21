'''_3997.py

SpiralBevelGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2283
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3868
from mastapy.system_model.analyses_and_results.power_flows.compound import _3914
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'SpiralBevelGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearCompoundPowerFlow',)


class SpiralBevelGearCompoundPowerFlow(_3914.BevelGearCompoundPowerFlow):
    '''SpiralBevelGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2283.SpiralBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3868.SpiralBevelGearPowerFlow]':
        '''List[SpiralBevelGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3868.SpiralBevelGearPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3868.SpiralBevelGearPowerFlow]':
        '''List[SpiralBevelGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3868.SpiralBevelGearPowerFlow))
        return value
