'''_61.py

FENodeOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FE_NODE_OPTION = python_net_import('SMT.MastaAPI.NodalAnalysis', 'FENodeOption')


__docformat__ = 'restructuredtext en'
__all__ = ('FENodeOption',)


class FENodeOption(Enum):
    '''FENodeOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FE_NODE_OPTION

    __hash__ = None

    NONE = 0
    SURFACE = 1
    ALL = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FENodeOption.__setattr__ = __enum_setattr
FENodeOption.__delattr__ = __enum_delattr
