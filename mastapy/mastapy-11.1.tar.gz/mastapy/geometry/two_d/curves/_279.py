'''_279.py

BasicCurveTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BASIC_CURVE_TYPES = python_net_import('SMT.MastaAPI.Geometry.TwoD.Curves', 'BasicCurveTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('BasicCurveTypes',)


class BasicCurveTypes(Enum):
    '''BasicCurveTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BASIC_CURVE_TYPES

    __hash__ = None

    NONE = 0
    LINEAR = 1
    PARABOLIC = 2
    CUBIC = 3
    CATMULLROM = 4
    ELLIPTIC = 5
    ARC = 6
    INVOLUTE = 7
    TURNING_POINT = 8
    HELICOID_INVOLUTE = 9


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BasicCurveTypes.__setattr__ = __enum_setattr
BasicCurveTypes.__delattr__ = __enum_delattr
