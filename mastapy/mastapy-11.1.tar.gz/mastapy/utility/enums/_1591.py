'''_1591.py

ThreeDViewContourOptionFirstSelection
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_THREE_D_VIEW_CONTOUR_OPTION_FIRST_SELECTION = python_net_import('SMT.MastaAPI.Utility.Enums', 'ThreeDViewContourOptionFirstSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('ThreeDViewContourOptionFirstSelection',)


class ThreeDViewContourOptionFirstSelection(Enum):
    '''ThreeDViewContourOptionFirstSelection

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _THREE_D_VIEW_CONTOUR_OPTION_FIRST_SELECTION

    __hash__ = None

    NO_CONTOUR = 0
    STRAIN_ENERGY = 1
    KINETIC_ENERGY = 2
    DISPLACEMENT = 3
    FORCE = 4
    STRESS = 5
    FE_MESH = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ThreeDViewContourOptionFirstSelection.__setattr__ = __enum_setattr
ThreeDViewContourOptionFirstSelection.__delattr__ = __enum_delattr
