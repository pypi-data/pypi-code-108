'''_1281.py

RolledBeforeOrAfterHeatTreament
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROLLED_BEFORE_OR_AFTER_HEAT_TREAMENT = python_net_import('SMT.MastaAPI.Bolts', 'RolledBeforeOrAfterHeatTreament')


__docformat__ = 'restructuredtext en'
__all__ = ('RolledBeforeOrAfterHeatTreament',)


class RolledBeforeOrAfterHeatTreament(Enum):
    '''RolledBeforeOrAfterHeatTreament

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROLLED_BEFORE_OR_AFTER_HEAT_TREAMENT

    __hash__ = None

    ROLLED_BEFORE_HEAT_TREATMENT = 0
    ROLLED_AFTER_HEAT_TREATMENT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RolledBeforeOrAfterHeatTreament.__setattr__ = __enum_setattr
RolledBeforeOrAfterHeatTreament.__delattr__ = __enum_delattr
