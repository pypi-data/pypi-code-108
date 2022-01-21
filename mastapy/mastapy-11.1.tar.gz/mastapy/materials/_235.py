'''_235.py

LubricantViscosityClassISO
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LUBRICANT_VISCOSITY_CLASS_ISO = python_net_import('SMT.MastaAPI.Materials', 'LubricantViscosityClassISO')


__docformat__ = 'restructuredtext en'
__all__ = ('LubricantViscosityClassISO',)


class LubricantViscosityClassISO(Enum):
    '''LubricantViscosityClassISO

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LUBRICANT_VISCOSITY_CLASS_ISO

    __hash__ = None

    ISO_VG_12 = 12
    ISO_VG_17 = 17
    ISO_VG_22 = 22
    ISO_VG_23 = 23
    ISO_VG_32 = 32
    ISO_VG_46 = 46
    ISO_VG_68 = 68
    ISO_VG_100 = 100
    ISO_VG_150 = 150
    ISO_VG_220 = 220
    ISO_VG_320 = 320
    ISO_VG_460 = 460
    ISO_VG_680 = 680
    ISO_VG_1000 = 1000
    ISO_VG_1500 = 1500
    ISO_VG_2200 = 2200
    ISO_VG_3200 = 3200
    ISO_VG_6800 = 6800


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LubricantViscosityClassISO.__setattr__ = __enum_setattr
LubricantViscosityClassISO.__delattr__ = __enum_delattr
