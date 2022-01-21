'''_3841.py

MassDiscPowerFlow
'''


from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6638
from mastapy.system_model.analyses_and_results.power_flows import _3891
from mastapy._internal.python_net import python_net_import

_MASS_DISC_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'MassDiscPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscPowerFlow',)


class MassDiscPowerFlow(_3891.VirtualComponentPowerFlow):
    '''MassDiscPowerFlow

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6638.MassDiscLoadCase':
        '''MassDiscLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6638.MassDiscLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
