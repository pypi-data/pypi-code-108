'''_1932.py

CylindricalHousingJournalBearing
'''


from mastapy.bearings.bearing_designs.fluid_film import _1939
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_HOUSING_JOURNAL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'CylindricalHousingJournalBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalHousingJournalBearing',)


class CylindricalHousingJournalBearing(_1939.PlainJournalHousing):
    '''CylindricalHousingJournalBearing

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_HOUSING_JOURNAL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalHousingJournalBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
