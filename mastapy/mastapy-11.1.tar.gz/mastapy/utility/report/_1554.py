'''_1554.py

DefinitionBooleanCheckOptions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DEFINITION_BOOLEAN_CHECK_OPTIONS = python_net_import('SMT.MastaAPI.Utility.Report', 'DefinitionBooleanCheckOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('DefinitionBooleanCheckOptions',)


class DefinitionBooleanCheckOptions(Enum):
    '''DefinitionBooleanCheckOptions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DEFINITION_BOOLEAN_CHECK_OPTIONS

    __hash__ = None

    NONE = 0
    INCLUDE_IF = 1
    EXCLUDE_IF = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DefinitionBooleanCheckOptions.__setattr__ = __enum_setattr
DefinitionBooleanCheckOptions.__delattr__ = __enum_delattr
