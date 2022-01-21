'''_246.py

QualityGrade
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_QUALITY_GRADE = python_net_import('SMT.MastaAPI.Materials', 'QualityGrade')


__docformat__ = 'restructuredtext en'
__all__ = ('QualityGrade',)


class QualityGrade(Enum):
    '''QualityGrade

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _QUALITY_GRADE

    __hash__ = None

    ML = 0
    MQ = 1
    ME = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


QualityGrade.__setattr__ = __enum_setattr
QualityGrade.__delattr__ = __enum_delattr
