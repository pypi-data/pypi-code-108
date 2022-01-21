'''_534.py

LocationOfEvaluationUpperLimit
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOCATION_OF_EVALUATION_UPPER_LIMIT = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'LocationOfEvaluationUpperLimit')


__docformat__ = 'restructuredtext en'
__all__ = ('LocationOfEvaluationUpperLimit',)


class LocationOfEvaluationUpperLimit(Enum):
    '''LocationOfEvaluationUpperLimit

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOCATION_OF_EVALUATION_UPPER_LIMIT

    __hash__ = None

    USERSPECIFIED = 0
    TIP_FORM = 1
    START_OF_TIP_RELIEF = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LocationOfEvaluationUpperLimit.__setattr__ = __enum_setattr
LocationOfEvaluationUpperLimit.__delattr__ = __enum_delattr
