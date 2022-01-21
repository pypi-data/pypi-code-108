'''_244.py

OilFiltrationOptions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_OIL_FILTRATION_OPTIONS = python_net_import('SMT.MastaAPI.Materials', 'OilFiltrationOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('OilFiltrationOptions',)


class OilFiltrationOptions(Enum):
    '''OilFiltrationOptions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _OIL_FILTRATION_OPTIONS

    __hash__ = None

    _1310_ISO_44061999_FILTER_RATING_995_FILTRATION_OF_6_MICRON_PARTICLES_ISO_16889 = 0
    _1512_ISO_44061999_FILTER_RATING_995_FILTRATION_OF_12_MICRON_PARTICLES_ISO_16889 = 1
    _1714_ISO_44061999_FILTER_RATING_987_FILTRATION_OF_25_MICRON_PARTICLES_ISO_16889 = 2
    _1916_ISO_44061999_FILTER_RATING_987_FILTRATION_OF_40_MICRON_PARTICLES_ISO_16889 = 3
    _1310_ISO_44061999_NO_FILTRATION = 4
    _1512_ISO_44061999_NO_FILTRATION = 5
    _1714_ISO_44061999_NO_FILTRATION = 6
    _1916_ISO_44061999_NO_FILTRATION = 7
    _2118_ISO_44061999_NO_FILTRATION = 8


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


OilFiltrationOptions.__setattr__ = __enum_setattr
OilFiltrationOptions.__delattr__ = __enum_delattr
