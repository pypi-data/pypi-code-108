'''_1332.py

TranslationRotation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TRANSLATION_ROTATION = python_net_import('SMT.MastaAPI.MathUtility', 'TranslationRotation')


__docformat__ = 'restructuredtext en'
__all__ = ('TranslationRotation',)


class TranslationRotation(Enum):
    '''TranslationRotation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TRANSLATION_ROTATION

    __hash__ = None

    TRANSLATION = 0
    ROTATION = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TranslationRotation.__setattr__ = __enum_setattr
TranslationRotation.__delattr__ = __enum_delattr
