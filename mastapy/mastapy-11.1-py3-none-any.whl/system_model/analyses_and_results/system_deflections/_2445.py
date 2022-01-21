'''_2445.py

BoltSystemDeflection
'''


from mastapy.system_model.part_model import _2184
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6546
from mastapy.system_model.analyses_and_results.power_flows import _3785
from mastapy.system_model.analyses_and_results.system_deflections import _2450
from mastapy._internal.python_net import python_net_import

_BOLT_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'BoltSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltSystemDeflection',)


class BoltSystemDeflection(_2450.ComponentSystemDeflection):
    '''BoltSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BOLT_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2184.Bolt':
        '''Bolt: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2184.Bolt)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6546.BoltLoadCase':
        '''BoltLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6546.BoltLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def power_flow_results(self) -> '_3785.BoltPowerFlow':
        '''BoltPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3785.BoltPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None
