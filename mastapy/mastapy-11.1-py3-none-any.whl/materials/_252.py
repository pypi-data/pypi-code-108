'''_252.py

SoundPressureEnclosureType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SOUND_PRESSURE_ENCLOSURE_TYPE = python_net_import('SMT.MastaAPI.Materials', 'SoundPressureEnclosureType')


__docformat__ = 'restructuredtext en'
__all__ = ('SoundPressureEnclosureType',)


class SoundPressureEnclosureType(Enum):
    '''SoundPressureEnclosureType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SOUND_PRESSURE_ENCLOSURE_TYPE

    __hash__ = None

    FREE_FIELD = 0
    FREE_FIELD_OVER_REFLECTING_PLANE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SoundPressureEnclosureType.__setattr__ = __enum_setattr
SoundPressureEnclosureType.__delattr__ = __enum_delattr
