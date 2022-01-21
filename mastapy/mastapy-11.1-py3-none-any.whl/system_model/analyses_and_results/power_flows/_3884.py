'''_3884.py

SynchroniserSleevePowerFlow
'''


from mastapy.system_model.part_model.couplings import _2346
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6689
from mastapy.system_model.analyses_and_results.power_flows import _3882
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_SLEEVE_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'SynchroniserSleevePowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserSleevePowerFlow',)


class SynchroniserSleevePowerFlow(_3882.SynchroniserPartPowerFlow):
    '''SynchroniserSleevePowerFlow

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_SLEEVE_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserSleevePowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2346.SynchroniserSleeve':
        '''SynchroniserSleeve: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2346.SynchroniserSleeve)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6689.SynchroniserSleeveLoadCase':
        '''SynchroniserSleeveLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6689.SynchroniserSleeveLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
