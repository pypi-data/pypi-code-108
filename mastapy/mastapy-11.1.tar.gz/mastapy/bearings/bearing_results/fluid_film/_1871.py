'''_1871.py

LoadedPlainJournalBearingResults
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_results.fluid_film import _1872, _1868
from mastapy._internal.python_net import python_net_import

_LOADED_PLAIN_JOURNAL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedPlainJournalBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedPlainJournalBearingResults',)


class LoadedPlainJournalBearingResults(_1868.LoadedFluidFilmBearingResults):
    '''LoadedPlainJournalBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_PLAIN_JOURNAL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedPlainJournalBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def operating_temperature(self) -> 'float':
        '''float: 'OperatingTemperature' is the original name of this property.'''

        return self.wrapped.OperatingTemperature

    @operating_temperature.setter
    def operating_temperature(self, value: 'float'):
        self.wrapped.OperatingTemperature = float(value) if value else 0.0

    @property
    def lubricant_density(self) -> 'float':
        '''float: 'LubricantDensity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDensity

    @property
    def kinematic_viscosity(self) -> 'float':
        '''float: 'KinematicViscosity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.KinematicViscosity

    @property
    def angular_position_of_the_minimum_film_thickness_from_the_x_axis(self) -> 'float':
        '''float: 'AngularPositionOfTheMinimumFilmThicknessFromTheXAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularPositionOfTheMinimumFilmThicknessFromTheXAxis

    @property
    def shaft_relative_rotation_speed(self) -> 'float':
        '''float: 'ShaftRelativeRotationSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftRelativeRotationSpeed

    @property
    def eccentricity_ratio(self) -> 'float':
        '''float: 'EccentricityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EccentricityRatio

    @property
    def minimum_central_film_thickness(self) -> 'float':
        '''float: 'MinimumCentralFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumCentralFilmThickness

    @property
    def attitude_angle(self) -> 'float':
        '''float: 'AttitudeAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AttitudeAngle

    @property
    def attitude_force(self) -> 'float':
        '''float: 'AttitudeForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AttitudeForce

    @property
    def non_dimensional_load(self) -> 'float':
        '''float: 'NonDimensionalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalLoad

    @property
    def pressure_velocity(self) -> 'float':
        '''float: 'PressureVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PressureVelocity

    @property
    def radial_load_per_unit_of_projected_area(self) -> 'float':
        '''float: 'RadialLoadPerUnitOfProjectedArea' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialLoadPerUnitOfProjectedArea

    @property
    def non_dimensional_power_loss(self) -> 'float':
        '''float: 'NonDimensionalPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalPowerLoss

    @property
    def journal_bearing_rows(self) -> 'List[_1872.LoadedPlainJournalBearingRow]':
        '''List[LoadedPlainJournalBearingRow]: 'JournalBearingRows' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.JournalBearingRows, constructor.new(_1872.LoadedPlainJournalBearingRow))
        return value
