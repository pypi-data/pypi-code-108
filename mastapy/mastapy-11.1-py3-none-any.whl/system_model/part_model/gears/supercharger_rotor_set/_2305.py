'''_2305.py

YVariableForImportedData
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_Y_VARIABLE_FOR_IMPORTED_DATA = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears.SuperchargerRotorSet', 'YVariableForImportedData')


__docformat__ = 'restructuredtext en'
__all__ = ('YVariableForImportedData',)


class YVariableForImportedData(Enum):
    '''YVariableForImportedData

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _Y_VARIABLE_FOR_IMPORTED_DATA

    __hash__ = None

    PRESSURE_RATIO = 0
    BOOST_PRESSURE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


YVariableForImportedData.__setattr__ = __enum_setattr
YVariableForImportedData.__delattr__ = __enum_delattr
