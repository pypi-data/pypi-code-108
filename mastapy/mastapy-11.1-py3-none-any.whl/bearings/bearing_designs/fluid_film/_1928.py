'''_1928.py

AxialFeedJournalBearing
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_AXIAL_FEED_JOURNAL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'AxialFeedJournalBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialFeedJournalBearing',)


class AxialFeedJournalBearing(_0.APIBase):
    '''AxialFeedJournalBearing

    This is a mastapy class.
    '''

    TYPE = _AXIAL_FEED_JOURNAL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AxialFeedJournalBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def groove_angular_location(self) -> 'float':
        '''float: 'GrooveAngularLocation' is the original name of this property.'''

        return self.wrapped.GrooveAngularLocation

    @groove_angular_location.setter
    def groove_angular_location(self, value: 'float'):
        self.wrapped.GrooveAngularLocation = float(value) if value else 0.0
