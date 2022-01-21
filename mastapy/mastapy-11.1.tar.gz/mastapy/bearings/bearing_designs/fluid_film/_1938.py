'''_1938.py

PlainJournalBearing
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_designs import _1880
from mastapy._internal.python_net import python_net_import

_PLAIN_JOURNAL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'PlainJournalBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('PlainJournalBearing',)


class PlainJournalBearing(_1880.DetailedBearing):
    '''PlainJournalBearing

    This is a mastapy class.
    '''

    TYPE = _PLAIN_JOURNAL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlainJournalBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diametrical_clearance(self) -> 'float':
        '''float: 'DiametricalClearance' is the original name of this property.'''

        return self.wrapped.DiametricalClearance

    @diametrical_clearance.setter
    def diametrical_clearance(self, value: 'float'):
        self.wrapped.DiametricalClearance = float(value) if value else 0.0

    @property
    def land_width(self) -> 'float':
        '''float: 'LandWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LandWidth

    @property
    def land_width_to_diameter_ratio(self) -> 'float':
        '''float: 'LandWidthToDiameterRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LandWidthToDiameterRatio
