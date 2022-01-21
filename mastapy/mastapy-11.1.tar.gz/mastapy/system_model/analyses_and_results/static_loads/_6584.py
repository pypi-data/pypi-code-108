'''_6584.py

ElectricMachineDataImportType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_DATA_IMPORT_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ElectricMachineDataImportType')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineDataImportType',)


class ElectricMachineDataImportType(Enum):
    '''ElectricMachineDataImportType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ELECTRIC_MACHINE_DATA_IMPORT_TYPE

    __hash__ = None

    ALTAIR_FLUX = 0
    EXCEL = 1
    JMAG = 2
    MOTORCAD = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ElectricMachineDataImportType.__setattr__ = __enum_setattr
ElectricMachineDataImportType.__delattr__ = __enum_delattr
