'''_212.py

AGMAMaterialApplications
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_AGMA_MATERIAL_APPLICATIONS = python_net_import('SMT.MastaAPI.Materials', 'AGMAMaterialApplications')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAMaterialApplications',)


class AGMAMaterialApplications(Enum):
    '''AGMAMaterialApplications

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _AGMA_MATERIAL_APPLICATIONS

    __hash__ = None

    GENERAL_APPLICATION = 0
    CRITICAL_SERVICE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AGMAMaterialApplications.__setattr__ = __enum_setattr
AGMAMaterialApplications.__delattr__ = __enum_delattr
