'''_1877.py

LoadedTiltingPadThrustBearingResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.fluid_film import _1870
from mastapy._internal.python_net import python_net_import

_LOADED_TILTING_PAD_THRUST_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedTiltingPadThrustBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedTiltingPadThrustBearingResults',)


class LoadedTiltingPadThrustBearingResults(_1870.LoadedPadFluidFilmBearingResults):
    '''LoadedTiltingPadThrustBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_TILTING_PAD_THRUST_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedTiltingPadThrustBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial_internal_clearance(self) -> 'float':
        '''float: 'AxialInternalClearance' is the original name of this property.'''

        return self.wrapped.AxialInternalClearance

    @axial_internal_clearance.setter
    def axial_internal_clearance(self, value: 'float'):
        self.wrapped.AxialInternalClearance = float(value) if value else 0.0

    @property
    def oil_exit_temperature(self) -> 'float':
        '''float: 'OilExitTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OilExitTemperature

    @property
    def minimum_flow_rate(self) -> 'float':
        '''float: 'MinimumFlowRate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFlowRate

    @property
    def minimum_film_thickness(self) -> 'float':
        '''float: 'MinimumFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFilmThickness

    @property
    def maximum_pad_film_temperature(self) -> 'float':
        '''float: 'MaximumPadFilmTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPadFilmTemperature

    @property
    def maximum_bearing_temperature(self) -> 'float':
        '''float: 'MaximumBearingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumBearingTemperature

    @property
    def maximum_pad_load(self) -> 'float':
        '''float: 'MaximumPadLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPadLoad

    @property
    def average_pad_load(self) -> 'float':
        '''float: 'AveragePadLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AveragePadLoad

    @property
    def maximum_pad_specific_load(self) -> 'float':
        '''float: 'MaximumPadSpecificLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPadSpecificLoad

    @property
    def maximum_pressure_velocity(self) -> 'float':
        '''float: 'MaximumPressureVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPressureVelocity

    @property
    def maximum_reynolds_number(self) -> 'float':
        '''float: 'MaximumReynoldsNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumReynoldsNumber

    @property
    def mean_reynolds_number(self) -> 'float':
        '''float: 'MeanReynoldsNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanReynoldsNumber
