'''_1949.py

ComponentDampingOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COMPONENT_DAMPING_OPTION = python_net_import('SMT.MastaAPI.SystemModel', 'ComponentDampingOption')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentDampingOption',)


class ComponentDampingOption(Enum):
    '''ComponentDampingOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COMPONENT_DAMPING_OPTION

    __hash__ = None

    LOAD_CASE_GLOBAL_DAMPING = 0
    SPECIFIED = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ComponentDampingOption.__setattr__ = __enum_setattr
ComponentDampingOption.__delattr__ = __enum_delattr
