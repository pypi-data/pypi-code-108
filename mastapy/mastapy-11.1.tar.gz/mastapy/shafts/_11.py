'''_11.py

FkmMaterialGroup
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FKM_MATERIAL_GROUP = python_net_import('SMT.MastaAPI.Shafts', 'FkmMaterialGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('FkmMaterialGroup',)


class FkmMaterialGroup(Enum):
    '''FkmMaterialGroup

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FKM_MATERIAL_GROUP

    __hash__ = None

    CASE_HARDENING_STEEL = 0
    STAINLESS_STEEL = 1
    FORGING_STEEL = 2
    STEEL_OTHER_THAN_THESE = 3
    GS = 4
    GJS = 5
    GJM = 6
    GJL = 7
    WROUGHT_ALUMINIUM_ALLOYS = 8
    CAST_ALUMINIUM_ALLOYS = 9


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FkmMaterialGroup.__setattr__ = __enum_setattr
FkmMaterialGroup.__delattr__ = __enum_delattr
