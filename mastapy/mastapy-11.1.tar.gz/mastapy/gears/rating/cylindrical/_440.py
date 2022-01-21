'''_440.py

MisalignmentContactPatternEnhancements
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MISALIGNMENT_CONTACT_PATTERN_ENHANCEMENTS = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'MisalignmentContactPatternEnhancements')


__docformat__ = 'restructuredtext en'
__all__ = ('MisalignmentContactPatternEnhancements',)


class MisalignmentContactPatternEnhancements(Enum):
    '''MisalignmentContactPatternEnhancements

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MISALIGNMENT_CONTACT_PATTERN_ENHANCEMENTS

    __hash__ = None

    CONTACT_PATTERN_UNPROVEN = 0
    CONTACT_PATTERN_FAVOURABLE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MisalignmentContactPatternEnhancements.__setattr__ = __enum_setattr
MisalignmentContactPatternEnhancements.__delattr__ = __enum_delattr
