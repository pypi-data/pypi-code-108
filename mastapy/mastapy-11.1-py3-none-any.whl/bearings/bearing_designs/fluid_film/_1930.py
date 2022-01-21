'''_1930.py

AxialHoleJournalBearing
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_designs.fluid_film import _1928
from mastapy._internal.python_net import python_net_import

_AXIAL_HOLE_JOURNAL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'AxialHoleJournalBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialHoleJournalBearing',)


class AxialHoleJournalBearing(_1928.AxialFeedJournalBearing):
    '''AxialHoleJournalBearing

    This is a mastapy class.
    '''

    TYPE = _AXIAL_HOLE_JOURNAL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AxialHoleJournalBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hole_diameter(self) -> 'float':
        '''float: 'HoleDiameter' is the original name of this property.'''

        return self.wrapped.HoleDiameter

    @hole_diameter.setter
    def hole_diameter(self, value: 'float'):
        self.wrapped.HoleDiameter = float(value) if value else 0.0
