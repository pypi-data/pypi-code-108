'''_1378.py

ExternalFullFEFileOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_EXTERNAL_FULL_FE_FILE_OPTION = python_net_import('SMT.MastaAPI.Utility', 'ExternalFullFEFileOption')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalFullFEFileOption',)


class ExternalFullFEFileOption(Enum):
    '''ExternalFullFEFileOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _EXTERNAL_FULL_FE_FILE_OPTION

    __hash__ = None

    NONE = 0
    MESH = 1
    MESH_AND_EXPANSION_VECTORS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ExternalFullFEFileOption.__setattr__ = __enum_setattr
ExternalFullFEFileOption.__delattr__ = __enum_delattr
