'''_1933.py

MachineryEncasedJournalBearing
'''


from mastapy.bearings.bearing_designs.fluid_film import _1939
from mastapy._internal.python_net import python_net_import

_MACHINERY_ENCASED_JOURNAL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'MachineryEncasedJournalBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('MachineryEncasedJournalBearing',)


class MachineryEncasedJournalBearing(_1939.PlainJournalHousing):
    '''MachineryEncasedJournalBearing

    This is a mastapy class.
    '''

    TYPE = _MACHINERY_ENCASED_JOURNAL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MachineryEncasedJournalBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
