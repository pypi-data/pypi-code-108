'''_5395.py

SystemOptimiserTargets
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SYSTEM_OPTIMISER_TARGETS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups', 'SystemOptimiserTargets')


__docformat__ = 'restructuredtext en'
__all__ = ('SystemOptimiserTargets',)


class SystemOptimiserTargets(Enum):
    '''SystemOptimiserTargets

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SYSTEM_OPTIMISER_TARGETS

    __hash__ = None

    MINIMUM_FACE_WIDTH = 0
    MINIMUM_MASS = 1
    MINIMUM_WIDEST_FACE_WIDTH = 2
    CONTACT_RATIO_FIXED_FACE_WIDTH = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SystemOptimiserTargets.__setattr__ = __enum_setattr
SystemOptimiserTargets.__delattr__ = __enum_delattr
