'''_174.py

NoneSelectedAllOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_NONE_SELECTED_ALL_OPTION = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'NoneSelectedAllOption')


__docformat__ = 'restructuredtext en'
__all__ = ('NoneSelectedAllOption',)


class NoneSelectedAllOption(Enum):
    '''NoneSelectedAllOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _NONE_SELECTED_ALL_OPTION

    __hash__ = None

    NONE = 0
    SELECTED = 1
    ALL = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


NoneSelectedAllOption.__setattr__ = __enum_setattr
NoneSelectedAllOption.__delattr__ = __enum_delattr
