'''_6690.py

TEExcitationType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TE_EXCITATION_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'TEExcitationType')


__docformat__ = 'restructuredtext en'
__all__ = ('TEExcitationType',)


class TEExcitationType(Enum):
    '''TEExcitationType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TE_EXCITATION_TYPE

    __hash__ = None

    TRANSMISSION_ERROR = 0
    MISALIGNMENT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TEExcitationType.__setattr__ = __enum_setattr
TEExcitationType.__delattr__ = __enum_delattr
