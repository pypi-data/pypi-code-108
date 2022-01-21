'''_206.py

SoftwareUsedForReductionType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SOFTWARE_USED_FOR_REDUCTION_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis', 'SoftwareUsedForReductionType')


__docformat__ = 'restructuredtext en'
__all__ = ('SoftwareUsedForReductionType',)


class SoftwareUsedForReductionType(Enum):
    '''SoftwareUsedForReductionType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SOFTWARE_USED_FOR_REDUCTION_TYPE

    __hash__ = None

    MASTA = 0
    ABAQUS = 1
    ANSYS = 2
    NASTRAN = 3
    OPTISTRUCT = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SoftwareUsedForReductionType.__setattr__ = __enum_setattr
SoftwareUsedForReductionType.__delattr__ = __enum_delattr
