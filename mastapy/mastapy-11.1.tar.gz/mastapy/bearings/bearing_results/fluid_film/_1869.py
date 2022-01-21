'''_1869.py

LoadedGreaseFilledJournalBearingResults
'''


from mastapy.bearings.bearing_results.fluid_film import _1871
from mastapy._internal.python_net import python_net_import

_LOADED_GREASE_FILLED_JOURNAL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedGreaseFilledJournalBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedGreaseFilledJournalBearingResults',)


class LoadedGreaseFilledJournalBearingResults(_1871.LoadedPlainJournalBearingResults):
    '''LoadedGreaseFilledJournalBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_GREASE_FILLED_JOURNAL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedGreaseFilledJournalBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
