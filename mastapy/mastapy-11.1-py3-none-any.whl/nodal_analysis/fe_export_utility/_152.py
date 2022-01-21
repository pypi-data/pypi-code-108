'''_152.py

FEExportFormat
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FE_EXPORT_FORMAT = python_net_import('SMT.MastaAPI.NodalAnalysis.FeExportUtility', 'FEExportFormat')


__docformat__ = 'restructuredtext en'
__all__ = ('FEExportFormat',)


class FEExportFormat(Enum):
    '''FEExportFormat

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FE_EXPORT_FORMAT

    __hash__ = None

    ANSYS_APDL_INPUT_FILE = 0
    ANSYS_WORKBENCH_COMMANDS = 1
    ANSYS_APDL_INPUT_FILE_OUTPUT_SUB = 2
    NASTRAN_BULK_DATA_FILE_OUTPUT_PCH = 3
    NASTRAN_BULK_DATA_FILE_OUTPUT_OP4_AND_PCH = 4
    ABAQUS_INPUT_FILE_OUTPUT_MTX = 5
    ABAQUS_INPUT_FILE_OUTPUT_FIL = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FEExportFormat.__setattr__ = __enum_setattr
FEExportFormat.__delattr__ = __enum_delattr
