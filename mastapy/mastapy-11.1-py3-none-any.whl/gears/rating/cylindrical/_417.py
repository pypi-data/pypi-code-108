'''_417.py

AGMAScuffingResultsRow
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical import _445
from mastapy._internal.python_net import python_net_import

_AGMA_SCUFFING_RESULTS_ROW = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'AGMAScuffingResultsRow')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAScuffingResultsRow',)


class AGMAScuffingResultsRow(_445.ScuffingResultsRow):
    '''AGMAScuffingResultsRow

    This is a mastapy class.
    '''

    TYPE = _AGMA_SCUFFING_RESULTS_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAScuffingResultsRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mean_coefficient_of_friction(self) -> 'float':
        '''float: 'MeanCoefficientOfFriction' is the original name of this property.'''

        return self.wrapped.MeanCoefficientOfFriction

    @mean_coefficient_of_friction.setter
    def mean_coefficient_of_friction(self, value: 'float'):
        self.wrapped.MeanCoefficientOfFriction = float(value) if value else 0.0

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
    def semi_width_of_hertzian_contact_band(self) -> 'float':
        '''float: 'SemiWidthOfHertzianContactBand' is the original name of this property.'''

        return self.wrapped.SemiWidthOfHertzianContactBand

    @semi_width_of_hertzian_contact_band.setter
    def semi_width_of_hertzian_contact_band(self, value: 'float'):
        self.wrapped.SemiWidthOfHertzianContactBand = float(value) if value else 0.0

    @property
    def speed_parameter(self) -> 'float':
        '''float: 'SpeedParameter' is the original name of this property.'''

        return self.wrapped.SpeedParameter

    @speed_parameter.setter
    def speed_parameter(self, value: 'float'):
        self.wrapped.SpeedParameter = float(value) if value else 0.0

    @property
    def load_parameter(self) -> 'float':
        '''float: 'LoadParameter' is the original name of this property.'''

        return self.wrapped.LoadParameter

    @load_parameter.setter
    def load_parameter(self, value: 'float'):
        self.wrapped.LoadParameter = float(value) if value else 0.0

    @property
    def dimensionless_central_film_thickness(self) -> 'float':
        '''float: 'DimensionlessCentralFilmThickness' is the original name of this property.'''

        return self.wrapped.DimensionlessCentralFilmThickness

    @dimensionless_central_film_thickness.setter
    def dimensionless_central_film_thickness(self, value: 'float'):
        self.wrapped.DimensionlessCentralFilmThickness = float(value) if value else 0.0

    @property
    def central_film_thickness(self) -> 'float':
        '''float: 'CentralFilmThickness' is the original name of this property.'''

        return self.wrapped.CentralFilmThickness

    @central_film_thickness.setter
    def central_film_thickness(self, value: 'float'):
        self.wrapped.CentralFilmThickness = float(value) if value else 0.0

    @property
    def specific_film_thickness_with_filter_cutoff_wave_length(self) -> 'float':
        '''float: 'SpecificFilmThicknessWithFilterCutoffWaveLength' is the original name of this property.'''

        return self.wrapped.SpecificFilmThicknessWithFilterCutoffWaveLength

    @specific_film_thickness_with_filter_cutoff_wave_length.setter
    def specific_film_thickness_with_filter_cutoff_wave_length(self, value: 'float'):
        self.wrapped.SpecificFilmThicknessWithFilterCutoffWaveLength = float(value) if value else 0.0
