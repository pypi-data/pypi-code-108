'''_1935.py

PedestalJournalBearing
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_designs.fluid_film import _1939
from mastapy._internal.python_net import python_net_import

_PEDESTAL_JOURNAL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'PedestalJournalBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('PedestalJournalBearing',)


class PedestalJournalBearing(_1939.PlainJournalHousing):
    '''PedestalJournalBearing

    This is a mastapy class.
    '''

    TYPE = _PEDESTAL_JOURNAL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PedestalJournalBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pedestal_base_depth(self) -> 'float':
        '''float: 'PedestalBaseDepth' is the original name of this property.'''

        return self.wrapped.PedestalBaseDepth

    @pedestal_base_depth.setter
    def pedestal_base_depth(self, value: 'float'):
        self.wrapped.PedestalBaseDepth = float(value) if value else 0.0
