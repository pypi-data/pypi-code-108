'''_2320.py

ClutchType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CLUTCH_TYPE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ClutchType')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchType',)


class ClutchType(Enum):
    '''ClutchType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CLUTCH_TYPE

    __hash__ = None

    CONCEPT_CLUTCH = 0
    MULTIPLATE_CLUTCH = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ClutchType.__setattr__ = __enum_setattr
ClutchType.__delattr__ = __enum_delattr
