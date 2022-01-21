'''_169.py

FESelectionMode
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FE_SELECTION_MODE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FESelectionMode')


__docformat__ = 'restructuredtext en'
__all__ = ('FESelectionMode',)


class FESelectionMode(Enum):
    '''FESelectionMode

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FE_SELECTION_MODE

    __hash__ = None

    COMPONENT = 0
    NODE_INDIVIDUAL = 1
    NODE_REGION = 2
    SURFACE = 3
    FACE = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FESelectionMode.__setattr__ = __enum_setattr
FESelectionMode.__delattr__ = __enum_delattr
