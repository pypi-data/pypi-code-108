'''_1900.py

FourPointContactAngleDefinition
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FOUR_POINT_CONTACT_ANGLE_DEFINITION = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'FourPointContactAngleDefinition')


__docformat__ = 'restructuredtext en'
__all__ = ('FourPointContactAngleDefinition',)


class FourPointContactAngleDefinition(Enum):
    '''FourPointContactAngleDefinition

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FOUR_POINT_CONTACT_ANGLE_DEFINITION

    __hash__ = None

    AXIAL = 0
    RADIAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FourPointContactAngleDefinition.__setattr__ = __enum_setattr
FourPointContactAngleDefinition.__delattr__ = __enum_delattr
