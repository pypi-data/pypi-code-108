'''_172.py

MassMatrixType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MASS_MATRIX_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'MassMatrixType')


__docformat__ = 'restructuredtext en'
__all__ = ('MassMatrixType',)


class MassMatrixType(Enum):
    '''MassMatrixType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MASS_MATRIX_TYPE

    __hash__ = None

    DIAGONAL = 0
    CONSISTENT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MassMatrixType.__setattr__ = __enum_setattr
MassMatrixType.__delattr__ = __enum_delattr
