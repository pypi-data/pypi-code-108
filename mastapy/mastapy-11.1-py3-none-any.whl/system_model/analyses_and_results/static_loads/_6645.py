'''_6645.py

ParametricStudyType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ParametricStudyType')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyType',)


class ParametricStudyType(Enum):
    '''ParametricStudyType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PARAMETRIC_STUDY_TYPE

    __hash__ = None

    LINEAR_SWEEP = 0
    MONTE_CARLO = 1
    DESIGN_OF_EXPERIMENTS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ParametricStudyType.__setattr__ = __enum_setattr
ParametricStudyType.__delattr__ = __enum_delattr
