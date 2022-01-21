'''_281.py

AGMAToleranceStandard
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AGMA_TOLERANCE_STANDARD = python_net_import('SMT.MastaAPI.Gears', 'AGMAToleranceStandard')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAToleranceStandard',)


class AGMAToleranceStandard(Enum):
    '''AGMAToleranceStandard

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AGMA_TOLERANCE_STANDARD

    __hash__ = None

    AGMA_20151A01 = 0
    AGMA_2000A88 = 1
    ANSIAGMA_ISO_13281B14 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AGMAToleranceStandard.__setattr__ = __enum_setattr
AGMAToleranceStandard.__delattr__ = __enum_delattr
