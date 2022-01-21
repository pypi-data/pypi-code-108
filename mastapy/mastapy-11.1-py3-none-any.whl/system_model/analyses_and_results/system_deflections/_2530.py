'''_2530.py

RingPinsToDiscConnectionSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.connections_and_sockets.cycloidal import _2083
from mastapy.system_model.analyses_and_results.static_loads import _6662
from mastapy.system_model.analyses_and_results.power_flows import _3858
from mastapy.system_model.analyses_and_results.system_deflections import _2531, _2502
from mastapy._internal.python_net import python_net_import

_RING_PINS_TO_DISC_CONNECTION_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'RingPinsToDiscConnectionSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsToDiscConnectionSystemDeflection',)


class RingPinsToDiscConnectionSystemDeflection(_2502.InterMountableComponentConnectionSystemDeflection):
    '''RingPinsToDiscConnectionSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_TO_DISC_CONNECTION_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsToDiscConnectionSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def strain_energy(self) -> 'float':
        '''float: 'StrainEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrainEnergy

    @property
    def normal_deflections(self) -> 'List[float]':
        '''List[float]: 'NormalDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NormalDeflections)
        return value

    @property
    def number_of_pins_in_contact(self) -> 'int':
        '''int: 'NumberOfPinsInContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfPinsInContact

    @property
    def pin_with_maximum_contact_stress(self) -> 'int':
        '''int: 'PinWithMaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinWithMaximumContactStress

    @property
    def maximum_contact_stress_across_all_pins(self) -> 'float':
        '''float: 'MaximumContactStressAcrossAllPins' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStressAcrossAllPins

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
    def power_flow_results(self) -> '_3858.RingPinsToDiscConnectionPowerFlow':
        '''RingPinsToDiscConnectionPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3858.RingPinsToDiscConnectionPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def ring_pin_to_disc_contacts(self) -> 'List[_2531.RingPinToDiscContactReporting]':
        '''List[RingPinToDiscContactReporting]: 'RingPinToDiscContacts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPinToDiscContacts, constructor.new(_2531.RingPinToDiscContactReporting))
        return value
