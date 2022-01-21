'''_1876.py

LoadedTiltingPadJournalBearingResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.fluid_film import _1870
from mastapy._internal.python_net import python_net_import

_LOADED_TILTING_PAD_JOURNAL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedTiltingPadJournalBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedTiltingPadJournalBearingResults',)


class LoadedTiltingPadJournalBearingResults(_1870.LoadedPadFluidFilmBearingResults):
    '''LoadedTiltingPadJournalBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_TILTING_PAD_JOURNAL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedTiltingPadJournalBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def force_in_direction_of_eccentricity(self) -> 'float':
        '''float: 'ForceInDirectionOfEccentricity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceInDirectionOfEccentricity

    @property
    def effective_film_temperature(self) -> 'float':
        '''float: 'EffectiveFilmTemperature' is the original name of this property.'''

        return self.wrapped.EffectiveFilmTemperature

    @effective_film_temperature.setter
    def effective_film_temperature(self, value: 'float'):
        self.wrapped.EffectiveFilmTemperature = float(value) if value else 0.0

    @property
    def lubricant_density(self) -> 'float':
        '''float: 'LubricantDensity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDensity

    @property
    def lubricant_dynamic_viscosity(self) -> 'float':
        '''float: 'LubricantDynamicViscosity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LubricantDynamicViscosity

    @property
    def maximum_pressure(self) -> 'float':
        '''float: 'MaximumPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPressure

    @property
    def maximum_pressure_velocity(self) -> 'float':
        '''float: 'MaximumPressureVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPressureVelocity

    @property
    def critical_reynolds_number(self) -> 'float':
        '''float: 'CriticalReynoldsNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CriticalReynoldsNumber

    @property
    def reynolds_number(self) -> 'float':
        '''float: 'ReynoldsNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReynoldsNumber

    @property
    def inlet_flow(self) -> 'float':
        '''float: 'InletFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InletFlow

    @property
    def side_flow(self) -> 'float':
        '''float: 'SideFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SideFlow

    @property
    def exit_flow(self) -> 'float':
        '''float: 'ExitFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExitFlow

    @property
    def feed_flow_rate(self) -> 'float':
        '''float: 'FeedFlowRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FeedFlowRate

    @property
    def eccentricity_ratio(self) -> 'float':
        '''float: 'EccentricityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EccentricityRatio

    @property
    def maximum_pad_eccentricity_ratio(self) -> 'float':
        '''float: 'MaximumPadEccentricityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPadEccentricityRatio

    @property
    def relative_clearance(self) -> 'float':
        '''float: 'RelativeClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeClearance

    @property
    def angular_position_of_the_minimum_film_thickness_from_the_x_axis(self) -> 'float':
        '''float: 'AngularPositionOfTheMinimumFilmThicknessFromTheXAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularPositionOfTheMinimumFilmThicknessFromTheXAxis

    @property
    def pad_shape_factor(self) -> 'float':
        '''float: 'PadShapeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PadShapeFactor

    @property
    def hydrodynamic_preload_factor(self) -> 'float':
        '''float: 'HydrodynamicPreloadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HydrodynamicPreloadFactor

    @property
    def sommerfeld_number(self) -> 'float':
        '''float: 'SommerfeldNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SommerfeldNumber

    @property
    def non_dimensional_maximum_pressure(self) -> 'float':
        '''float: 'NonDimensionalMaximumPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalMaximumPressure

    @property
    def non_dimensional_minimum_film_thickness(self) -> 'float':
        '''float: 'NonDimensionalMinimumFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalMinimumFilmThickness

    @property
    def non_dimensional_friction(self) -> 'float':
        '''float: 'NonDimensionalFriction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalFriction

    @property
    def non_dimensional_side_flow(self) -> 'float':
        '''float: 'NonDimensionalSideFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalSideFlow

    @property
    def non_dimensional_out_flow(self) -> 'float':
        '''float: 'NonDimensionalOutFlow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalOutFlow

    @property
    def minimum_film_thickness(self) -> 'float':
        '''float: 'MinimumFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFilmThickness
