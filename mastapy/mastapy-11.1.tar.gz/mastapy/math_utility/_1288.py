'''_1288.py

AcousticWeighting
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ACOUSTIC_WEIGHTING = python_net_import('SMT.MastaAPI.MathUtility', 'AcousticWeighting')


__docformat__ = 'restructuredtext en'
__all__ = ('AcousticWeighting',)


class AcousticWeighting(Enum):
    '''AcousticWeighting

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ACOUSTIC_WEIGHTING

    __hash__ = None

    NONE = 0
    AWEIGHTING = 1
    BWEIGHTING = 2
    CWEIGHTING = 3
    DWEIGHTING = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AcousticWeighting.__setattr__ = __enum_setattr
AcousticWeighting.__delattr__ = __enum_delattr
