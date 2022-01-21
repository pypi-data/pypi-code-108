'''_1186.py

MaterialPropertyClass
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MATERIAL_PROPERTY_CLASS = python_net_import('SMT.MastaAPI.FETools.Enums', 'MaterialPropertyClass')


__docformat__ = 'restructuredtext en'
__all__ = ('MaterialPropertyClass',)


class MaterialPropertyClass(Enum):
    '''MaterialPropertyClass

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MATERIAL_PROPERTY_CLASS

    __hash__ = None

    ISOTROPIC = 0
    ORTHOTROPIC = 2
    ANISOTROPIC = 3
    HYPERELASTIC = 4
    UNKNOWN_CLASS = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MaterialPropertyClass.__setattr__ = __enum_setattr
MaterialPropertyClass.__delattr__ = __enum_delattr
