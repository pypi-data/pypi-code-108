'''_436.py

ISOScuffingResultsRow
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical import _445
from mastapy._internal.python_net import python_net_import

_ISO_SCUFFING_RESULTS_ROW = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'ISOScuffingResultsRow')


__docformat__ = 'restructuredtext en'
__all__ = ('ISOScuffingResultsRow',)


class ISOScuffingResultsRow(_445.ScuffingResultsRow):
    '''ISOScuffingResultsRow

    This is a mastapy class.
    '''

    TYPE = _ISO_SCUFFING_RESULTS_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISOScuffingResultsRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def flash_temperature(self) -> 'float':
        '''float: 'FlashTemperature' is the original name of this property.'''

        return self.wrapped.FlashTemperature

    @flash_temperature.setter
    def flash_temperature(self, value: 'float'):
        self.wrapped.FlashTemperature = float(value) if value else 0.0

    @property
    def contact_temperature(self) -> 'float':
        '''float: 'ContactTemperature' is the original name of this property.'''

        return self.wrapped.ContactTemperature

    @contact_temperature.setter
    def contact_temperature(self, value: 'float'):
        self.wrapped.ContactTemperature = float(value) if value else 0.0

    @property
    def sliding_velocity(self) -> 'float':
        '''float: 'SlidingVelocity' is the original name of this property.'''

        return self.wrapped.SlidingVelocity

    @sliding_velocity.setter
    def sliding_velocity(self, value: 'float'):
        self.wrapped.SlidingVelocity = float(value) if value else 0.0

    @property
    def pinion_rolling_velocity(self) -> 'float':
        '''float: 'PinionRollingVelocity' is the original name of this property.'''

        return self.wrapped.PinionRollingVelocity

    @pinion_rolling_velocity.setter
    def pinion_rolling_velocity(self, value: 'float'):
        self.wrapped.PinionRollingVelocity = float(value) if value else 0.0

    @property
    def wheel_rolling_velocity(self) -> 'float':
        '''float: 'WheelRollingVelocity' is the original name of this property.'''

        return self.wrapped.WheelRollingVelocity

    @wheel_rolling_velocity.setter
    def wheel_rolling_velocity(self, value: 'float'):
        self.wrapped.WheelRollingVelocity = float(value) if value else 0.0

    @property
    def approach_factor(self) -> 'float':
        '''float: 'ApproachFactor' is the original name of this property.'''

        return self.wrapped.ApproachFactor

    @approach_factor.setter
    def approach_factor(self, value: 'float'):
        self.wrapped.ApproachFactor = float(value) if value else 0.0

    @property
    def thermo_elastic_factor(self) -> 'float':
        '''float: 'ThermoElasticFactor' is the original name of this property.'''

        return self.wrapped.ThermoElasticFactor

    @thermo_elastic_factor.setter
    def thermo_elastic_factor(self, value: 'float'):
        self.wrapped.ThermoElasticFactor = float(value) if value else 0.0

    @property
    def geometry_factor(self) -> 'float':
        '''float: 'GeometryFactor' is the original name of this property.'''

        return self.wrapped.GeometryFactor

    @geometry_factor.setter
    def geometry_factor(self, value: 'float'):
        self.wrapped.GeometryFactor = float(value) if value else 0.0
