'''_213.py

AGMAMaterialClasses
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AGMA_MATERIAL_CLASSES = python_net_import('SMT.MastaAPI.Materials', 'AGMAMaterialClasses')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAMaterialClasses',)


class AGMAMaterialClasses(Enum):
    '''AGMAMaterialClasses

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AGMA_MATERIAL_CLASSES

    __hash__ = None

    STEEL_THROUGH_HARDENED = 0
    STEEL_FLAME_OR_INDUCTION_HARDENED_TYPE_A = 1
    STEEL_FLAME_OR_INDUCTION_HARDENED_TYPE_B = 2
    STEEL_CARBURIZED_HARDENED = 3
    STEEL_NITRIDED_THROUGH_HARDENED = 4
    STEEL_25_CHROME_NITRIDED = 5
    STEEL_NITRALLOY_135M_NITRIDED = 6
    STEEL_NITRALLOY_N_NITRIDED = 7
    ASTM_A48_GRAY_CAST_IRON_CLASS_20 = 8
    ASTM_A48_GRAY_CAST_IRON_CLASS_30 = 9
    ASTM_A48_GRAY_CAST_IRON_CLASS_40 = 10
    ASTM_A536_DUCTILE_IRON_GRADE_60 = 11
    ASTM_A536_DUCTILE_IRON_GRADE_80 = 12
    ASTM_A536_DUCTILE_IRON_GRADE_100 = 13
    ASTM_A536_DUCTILE_IRON_GRADE_120 = 14
    CUSTOM = 15


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AGMAMaterialClasses.__setattr__ = __enum_setattr
AGMAMaterialClasses.__delattr__ = __enum_delattr
