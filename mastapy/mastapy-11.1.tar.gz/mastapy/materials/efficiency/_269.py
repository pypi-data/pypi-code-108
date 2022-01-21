'''_269.py

OilSealMaterialType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_OIL_SEAL_MATERIAL_TYPE = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'OilSealMaterialType')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealMaterialType',)


class OilSealMaterialType(Enum):
    '''OilSealMaterialType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _OIL_SEAL_MATERIAL_TYPE

    __hash__ = None

    VITON = 0
    BUNAN = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


OilSealMaterialType.__setattr__ = __enum_setattr
OilSealMaterialType.__delattr__ = __enum_delattr
