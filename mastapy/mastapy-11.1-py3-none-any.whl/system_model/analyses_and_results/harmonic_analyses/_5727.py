'''_5727.py

ExportOutputType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_EXPORT_OUTPUT_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'ExportOutputType')


__docformat__ = 'restructuredtext en'
__all__ = ('ExportOutputType',)


class ExportOutputType(Enum):
    '''ExportOutputType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _EXPORT_OUTPUT_TYPE

    __hash__ = None

    BOUNDARY_CONDITIONS_TO_FE_SOLVER = 0
    BOUNDARY_CONDITIONS_AS_PLAIN_TEXT = 1
    OPERATING_DEFLECTION_SHAPES_AS_OP2_FILE = 2
    OPERATING_DEFLECTION_SHAPES_AS_PLAIN_TEXT = 3
    MODE_SHAPES_AS_OP2_FILE = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ExportOutputType.__setattr__ = __enum_setattr
ExportOutputType.__delattr__ = __enum_delattr
