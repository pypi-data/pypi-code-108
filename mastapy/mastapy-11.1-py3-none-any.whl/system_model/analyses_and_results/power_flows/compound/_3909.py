'''_3909.py

BevelDifferentialGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2255, _2257, _2258
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.power_flows import _3777
from mastapy.system_model.analyses_and_results.power_flows.compound import _3914
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'BevelDifferentialGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearCompoundPowerFlow',)


class BevelDifferentialGearCompoundPowerFlow(_3914.BevelGearCompoundPowerFlow):
    '''BevelDifferentialGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2255.BevelDifferentialGear':
        '''BevelDifferentialGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2255.BevelDifferentialGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BevelDifferentialGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3777.BevelDifferentialGearPowerFlow]':
        '''List[BevelDifferentialGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3777.BevelDifferentialGearPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3777.BevelDifferentialGearPowerFlow]':
        '''List[BevelDifferentialGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3777.BevelDifferentialGearPowerFlow))
        return value
