'''_538.py

MainProfileReliefEndsAtTheStartOfTipReliefOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MAIN_PROFILE_RELIEF_ENDS_AT_THE_START_OF_TIP_RELIEF_OPTION = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'MainProfileReliefEndsAtTheStartOfTipReliefOption')


__docformat__ = 'restructuredtext en'
__all__ = ('MainProfileReliefEndsAtTheStartOfTipReliefOption',)


class MainProfileReliefEndsAtTheStartOfTipReliefOption(Enum):
    '''MainProfileReliefEndsAtTheStartOfTipReliefOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MAIN_PROFILE_RELIEF_ENDS_AT_THE_START_OF_TIP_RELIEF_OPTION

    __hash__ = None

    NO = 0
    YES = 1
    ONLY_WHEN_NON_ZERO_TIP_RELIEF = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MainProfileReliefEndsAtTheStartOfTipReliefOption.__setattr__ = __enum_setattr
MainProfileReliefEndsAtTheStartOfTipReliefOption.__delattr__ = __enum_delattr
