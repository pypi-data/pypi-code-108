'''_151.py

BoundaryConditionType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BOUNDARY_CONDITION_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis.FeExportUtility', 'BoundaryConditionType')


__docformat__ = 'restructuredtext en'
__all__ = ('BoundaryConditionType',)


class BoundaryConditionType(Enum):
    '''BoundaryConditionType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BOUNDARY_CONDITION_TYPE

    __hash__ = None

    FORCE = 0
    DISPLACEMENT = 1
    NONE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BoundaryConditionType.__setattr__ = __enum_setattr
BoundaryConditionType.__delattr__ = __enum_delattr
