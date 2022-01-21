'''_1868.py

LoadedFluidFilmBearingResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results import _1708
from mastapy._internal.python_net import python_net_import

_LOADED_FLUID_FILM_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedFluidFilmBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedFluidFilmBearingResults',)


class LoadedFluidFilmBearingResults(_1708.LoadedDetailedBearingResults):
    '''LoadedFluidFilmBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_FLUID_FILM_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedFluidFilmBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relative_misalignment(self) -> 'float':
        '''float: 'RelativeMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMisalignment
