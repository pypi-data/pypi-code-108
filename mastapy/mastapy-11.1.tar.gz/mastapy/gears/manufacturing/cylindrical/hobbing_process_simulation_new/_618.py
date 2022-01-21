'''_618.py

ActiveProcessMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ACTIVE_PROCESS_METHOD = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'ActiveProcessMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('ActiveProcessMethod',)


class ActiveProcessMethod(Enum):
    '''ActiveProcessMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ACTIVE_PROCESS_METHOD

    __hash__ = None

    ROUGH_PROCESS_SIMULATION = 0
    FINISH_PROCESS_SIMULATION = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ActiveProcessMethod.__setattr__ = __enum_setattr
ActiveProcessMethod.__delattr__ = __enum_delattr
