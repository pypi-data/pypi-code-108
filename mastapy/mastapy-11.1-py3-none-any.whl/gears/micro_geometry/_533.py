'''_533.py

LocationOfEvaluationLowerLimit
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOCATION_OF_EVALUATION_LOWER_LIMIT = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'LocationOfEvaluationLowerLimit')


__docformat__ = 'restructuredtext en'
__all__ = ('LocationOfEvaluationLowerLimit',)


class LocationOfEvaluationLowerLimit(Enum):
    '''LocationOfEvaluationLowerLimit

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOCATION_OF_EVALUATION_LOWER_LIMIT

    __hash__ = None

    USERSPECIFIED = 0
    ROOT_FORM = 1
    START_OF_ROOT_RELIEF = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LocationOfEvaluationLowerLimit.__setattr__ = __enum_setattr
LocationOfEvaluationLowerLimit.__delattr__ = __enum_delattr
