'''_3987.py

RingPinsCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3857
from mastapy.system_model.analyses_and_results.power_flows.compound import _3975
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'RingPinsCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundPowerFlow',)


class RingPinsCompoundPowerFlow(_3975.MountableComponentCompoundPowerFlow):
    '''RingPinsCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3857.RingPinsPowerFlow]':
        '''List[RingPinsPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3857.RingPinsPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3857.RingPinsPowerFlow]':
        '''List[RingPinsPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3857.RingPinsPowerFlow))
        return value
