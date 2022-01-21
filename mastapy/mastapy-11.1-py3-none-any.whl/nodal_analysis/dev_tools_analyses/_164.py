'''_164.py

FEModelSetupViewType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FE_MODEL_SETUP_VIEW_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FEModelSetupViewType')


__docformat__ = 'restructuredtext en'
__all__ = ('FEModelSetupViewType',)


class FEModelSetupViewType(Enum):
    '''FEModelSetupViewType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FE_MODEL_SETUP_VIEW_TYPE

    __hash__ = None

    CURRENT_SETUP = 0
    REDUCTION_RESULT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FEModelSetupViewType.__setattr__ = __enum_setattr
FEModelSetupViewType.__delattr__ = __enum_delattr
