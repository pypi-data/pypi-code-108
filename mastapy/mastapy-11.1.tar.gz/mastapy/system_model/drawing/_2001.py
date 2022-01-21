'''_2001.py

StressResultOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_STRESS_RESULT_OPTION = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'StressResultOption')


__docformat__ = 'restructuredtext en'
__all__ = ('StressResultOption',)


class StressResultOption(Enum):
    '''StressResultOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _STRESS_RESULT_OPTION

    __hash__ = None

    ELEMENT_NODE = 0
    AVERAGE_TO_NODES = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


StressResultOption.__setattr__ = __enum_setattr
StressResultOption.__delattr__ = __enum_delattr
