'''_2201.py

LoadSharingModes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOAD_SHARING_MODES = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'LoadSharingModes')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadSharingModes',)


class LoadSharingModes(Enum):
    '''LoadSharingModes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOAD_SHARING_MODES

    __hash__ = None

    EQUAL = 0
    USER_DEFINED = 1
    AGMA_EMPIRICAL = 2
    GL = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LoadSharingModes.__setattr__ = __enum_setattr
LoadSharingModes.__delattr__ = __enum_delattr
