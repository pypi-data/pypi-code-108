'''_13.py

FkmVersionOfMinersRule
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FKM_VERSION_OF_MINERS_RULE = python_net_import('SMT.MastaAPI.Shafts', 'FkmVersionOfMinersRule')


__docformat__ = 'restructuredtext en'
__all__ = ('FkmVersionOfMinersRule',)


class FkmVersionOfMinersRule(Enum):
    '''FkmVersionOfMinersRule

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FKM_VERSION_OF_MINERS_RULE

    __hash__ = None

    CONSISTENT = 0
    ELEMENTARY = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FkmVersionOfMinersRule.__setattr__ = __enum_setattr
FkmVersionOfMinersRule.__delattr__ = __enum_delattr
