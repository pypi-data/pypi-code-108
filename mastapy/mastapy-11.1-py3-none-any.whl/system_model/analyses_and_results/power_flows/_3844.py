'''_3844.py

OilSealPowerFlow
'''


from mastapy.system_model.part_model import _2207
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6644
from mastapy.system_model.analyses_and_results.power_flows import _3801
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'OilSealPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealPowerFlow',)


class OilSealPowerFlow(_3801.ConnectorPowerFlow):
    '''OilSealPowerFlow

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2207.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6644.OilSealLoadCase':
        '''OilSealLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6644.OilSealLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
