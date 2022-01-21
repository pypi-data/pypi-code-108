'''_1675.py

RoundnessSpecificationType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROUNDNESS_SPECIFICATION_TYPE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'RoundnessSpecificationType')


__docformat__ = 'restructuredtext en'
__all__ = ('RoundnessSpecificationType',)


class RoundnessSpecificationType(Enum):
    '''RoundnessSpecificationType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROUNDNESS_SPECIFICATION_TYPE

    __hash__ = None

    SINUSOIDAL = 0
    USERSPECIFIED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RoundnessSpecificationType.__setattr__ = __enum_setattr
RoundnessSpecificationType.__delattr__ = __enum_delattr
