'''_3864.py

ShaftPowerFlow
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.analyses_and_results.static_loads import _6668
from mastapy.system_model.analyses_and_results.power_flows import _3767
from mastapy._internal.python_net import python_net_import

_SHAFT_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'ShaftPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftPowerFlow',)


class ShaftPowerFlow(_3767.AbstractShaftPowerFlow):
    '''ShaftPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SHAFT_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pin_tangential_oscillation_frequency(self) -> 'float':
        '''float: 'PinTangentialOscillationFrequency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinTangentialOscillationFrequency

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6668.ShaftLoadCase':
        '''ShaftLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6668.ShaftLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
