'''_4114.py

ParametricStudyDimension
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_DIMENSION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyDimension')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyDimension',)


class ParametricStudyDimension(Enum):
    '''ParametricStudyDimension

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PARAMETRIC_STUDY_DIMENSION

    __hash__ = None

    DIMENSION_1 = 1
    DIMENSION_2 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ParametricStudyDimension.__setattr__ = __enum_setattr
ParametricStudyDimension.__delattr__ = __enum_delattr
