'''_1937.py

PlainGreaseFilledJournalBearingHousingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PLAIN_GREASE_FILLED_JOURNAL_BEARING_HOUSING_TYPE = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'PlainGreaseFilledJournalBearingHousingType')


__docformat__ = 'restructuredtext en'
__all__ = ('PlainGreaseFilledJournalBearingHousingType',)


class PlainGreaseFilledJournalBearingHousingType(Enum):
    '''PlainGreaseFilledJournalBearingHousingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PLAIN_GREASE_FILLED_JOURNAL_BEARING_HOUSING_TYPE

    __hash__ = None

    MACHINERY_ENCASED = 0
    PEDESTAL_BASE = 1
    CYLINDRICAL_HOUSING = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PlainGreaseFilledJournalBearingHousingType.__setattr__ = __enum_setattr
PlainGreaseFilledJournalBearingHousingType.__delattr__ = __enum_delattr
