'''_1035.py

TipAlterationCoefficientMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TIP_ALTERATION_COEFFICIENT_METHOD = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'TipAlterationCoefficientMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('TipAlterationCoefficientMethod',)


class TipAlterationCoefficientMethod(Enum):
    '''TipAlterationCoefficientMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TIP_ALTERATION_COEFFICIENT_METHOD

    __hash__ = None

    USERSPECIFIED = 0
    B = 1
    C = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TipAlterationCoefficientMethod.__setattr__ = __enum_setattr
TipAlterationCoefficientMethod.__delattr__ = __enum_delattr
