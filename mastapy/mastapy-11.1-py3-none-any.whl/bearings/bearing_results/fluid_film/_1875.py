'''_1875.py

LoadedTiltingJournalPad
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.fluid_film import _1867
from mastapy._internal.python_net import python_net_import

_LOADED_TILTING_JOURNAL_PAD = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedTiltingJournalPad')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedTiltingJournalPad',)


class LoadedTiltingJournalPad(_1867.LoadedFluidFilmBearingPad):
    '''LoadedTiltingJournalPad

    This is a mastapy class.
    '''

    TYPE = _LOADED_TILTING_JOURNAL_PAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedTiltingJournalPad.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def eccentricity_ratio(self) -> 'float':
        '''float: 'EccentricityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EccentricityRatio

    @property
    def minimum_lubricant_film_thickness(self) -> 'float':
        '''float: 'MinimumLubricantFilmThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricantFilmThickness
