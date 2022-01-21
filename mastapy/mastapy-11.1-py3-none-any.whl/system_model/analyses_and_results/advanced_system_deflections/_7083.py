'''_7083.py

RingPinsToDiscConnectionAdvancedSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.connections_and_sockets.cycloidal import _2083
from mastapy.system_model.analyses_and_results.static_loads import _6662
from mastapy.system_model.analyses_and_results.system_deflections import _2530
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7057
from mastapy._internal.python_net import python_net_import

_RING_PINS_TO_DISC_CONNECTION_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'RingPinsToDiscConnectionAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsToDiscConnectionAdvancedSystemDeflection',)


class RingPinsToDiscConnectionAdvancedSystemDeflection(_7057.InterMountableComponentConnectionAdvancedSystemDeflection):
    '''RingPinsToDiscConnectionAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_TO_DISC_CONNECTION_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsToDiscConnectionAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def average_number_of_pins_in_contact(self) -> 'float':
        '''float: 'AverageNumberOfPinsInContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageNumberOfPinsInContact

    @property
    def maximum_contact_stress(self) -> 'float':
        '''float: 'MaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStress

    @property
    def connection_design(self) -> '_2083.RingPinsToDiscConnection':
        '''RingPinsToDiscConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2083.RingPinsToDiscConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6662.RingPinsToDiscConnectionLoadCase':
        '''RingPinsToDiscConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6662.RingPinsToDiscConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def connection_system_deflection_results(self) -> 'List[_2530.RingPinsToDiscConnectionSystemDeflection]':
        '''List[RingPinsToDiscConnectionSystemDeflection]: 'ConnectionSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionSystemDeflectionResults, constructor.new(_2530.RingPinsToDiscConnectionSystemDeflection))
        return value
