'''_1969.py

TransmissionTemperatureSet
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TRANSMISSION_TEMPERATURE_SET = python_net_import('SMT.MastaAPI.SystemModel', 'TransmissionTemperatureSet')


__docformat__ = 'restructuredtext en'
__all__ = ('TransmissionTemperatureSet',)


class TransmissionTemperatureSet(_0.APIBase):
    '''TransmissionTemperatureSet

    This is a mastapy class.
    '''

    TYPE = _TRANSMISSION_TEMPERATURE_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TransmissionTemperatureSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rolling_bearing_element(self) -> 'float':
        '''float: 'RollingBearingElement' is the original name of this property.'''

        return self.wrapped.RollingBearingElement

    @rolling_bearing_element.setter
    def rolling_bearing_element(self, value: 'float'):
        self.wrapped.RollingBearingElement = float(value) if value else 0.0

    @property
    def rolling_bearing_inner_race(self) -> 'float':
        '''float: 'RollingBearingInnerRace' is the original name of this property.'''

        return self.wrapped.RollingBearingInnerRace

    @rolling_bearing_inner_race.setter
    def rolling_bearing_inner_race(self, value: 'float'):
        self.wrapped.RollingBearingInnerRace = float(value) if value else 0.0

    @property
    def rolling_bearing_outer_race(self) -> 'float':
        '''float: 'RollingBearingOuterRace' is the original name of this property.'''

        return self.wrapped.RollingBearingOuterRace

    @rolling_bearing_outer_race.setter
    def rolling_bearing_outer_race(self, value: 'float'):
        self.wrapped.RollingBearingOuterRace = float(value) if value else 0.0

    @property
    def temperature_when_assembled(self) -> 'float':
        '''float: 'TemperatureWhenAssembled' is the original name of this property.'''

        return self.wrapped.TemperatureWhenAssembled

    @temperature_when_assembled.setter
    def temperature_when_assembled(self, value: 'float'):
        self.wrapped.TemperatureWhenAssembled = float(value) if value else 0.0

    @property
    def air_temperature(self) -> 'float':
        '''float: 'AirTemperature' is the original name of this property.'''

        return self.wrapped.AirTemperature

    @air_temperature.setter
    def air_temperature(self, value: 'float'):
        self.wrapped.AirTemperature = float(value) if value else 0.0

    @property
    def housing(self) -> 'float':
        '''float: 'Housing' is the original name of this property.'''

        return self.wrapped.Housing

    @housing.setter
    def housing(self, value: 'float'):
        self.wrapped.Housing = float(value) if value else 0.0

    @property
    def shaft(self) -> 'float':
        '''float: 'Shaft' is the original name of this property.'''

        return self.wrapped.Shaft

    @shaft.setter
    def shaft(self, value: 'float'):
        self.wrapped.Shaft = float(value) if value else 0.0

    @property
    def oil_sump_and_inlet_temperature(self) -> 'float':
        '''float: 'OilSumpAndInletTemperature' is the original name of this property.'''

        return self.wrapped.OilSumpAndInletTemperature

    @oil_sump_and_inlet_temperature.setter
    def oil_sump_and_inlet_temperature(self, value: 'float'):
        self.wrapped.OilSumpAndInletTemperature = float(value) if value else 0.0
