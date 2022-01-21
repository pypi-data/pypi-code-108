'''_1385.py

LoadCaseOverrideOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOAD_CASE_OVERRIDE_OPTION = python_net_import('SMT.MastaAPI.Utility', 'LoadCaseOverrideOption')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadCaseOverrideOption',)


class LoadCaseOverrideOption(Enum):
    '''LoadCaseOverrideOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOAD_CASE_OVERRIDE_OPTION

    __hash__ = None

    LOAD_CASE_SETTING = 0
    YES = 1
    NO = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LoadCaseOverrideOption.__setattr__ = __enum_setattr
LoadCaseOverrideOption.__delattr__ = __enum_delattr
