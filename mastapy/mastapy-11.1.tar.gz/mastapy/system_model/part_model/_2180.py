'''_2180.py

AGMALoadSharingTableApplicationLevel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AGMA_LOAD_SHARING_TABLE_APPLICATION_LEVEL = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AGMALoadSharingTableApplicationLevel')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMALoadSharingTableApplicationLevel',)


class AGMALoadSharingTableApplicationLevel(Enum):
    '''AGMALoadSharingTableApplicationLevel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AGMA_LOAD_SHARING_TABLE_APPLICATION_LEVEL

    __hash__ = None

    APPLICATION_LEVEL_1 = 0
    APPLICATION_LEVEL_2 = 1
    APPLICATION_LEVEL_3 = 2
    APPLICATION_LEVEL_4 = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AGMALoadSharingTableApplicationLevel.__setattr__ = __enum_setattr
AGMALoadSharingTableApplicationLevel.__delattr__ = __enum_delattr
