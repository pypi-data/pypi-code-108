'''_1870.py

LoadedPadFluidFilmBearingResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.fluid_film import _1868
from mastapy._internal.python_net import python_net_import

_LOADED_PAD_FLUID_FILM_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedPadFluidFilmBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedPadFluidFilmBearingResults',)


class LoadedPadFluidFilmBearingResults(_1868.LoadedFluidFilmBearingResults):
    '''LoadedPadFluidFilmBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_PAD_FLUID_FILM_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedPadFluidFilmBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum_film_thickness(self) -> 'float':
        '''float: 'MinimumFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFilmThickness

    @property
    def sliding_speed(self) -> 'float':
        '''float: 'SlidingSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingSpeed

    @property
    def oil_inlet_temperature(self) -> 'float':
        '''float: 'OilInletTemperature' is the original name of this property.'''

        return self.wrapped.OilInletTemperature

    @oil_inlet_temperature.setter
    def oil_inlet_temperature(self, value: 'float'):
        self.wrapped.OilInletTemperature = float(value) if value else 0.0

    @property
    def reynolds_number(self) -> 'float':
        '''float: 'ReynoldsNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReynoldsNumber
