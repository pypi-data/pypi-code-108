'''_1179.py

ContactPairConstrainedSurfaceType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONTACT_PAIR_CONSTRAINED_SURFACE_TYPE = python_net_import('SMT.MastaAPI.FETools.VisToolsGlobal.VisToolsGlobalEnums', 'ContactPairConstrainedSurfaceType')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactPairConstrainedSurfaceType',)


class ContactPairConstrainedSurfaceType(Enum):
    '''ContactPairConstrainedSurfaceType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONTACT_PAIR_CONSTRAINED_SURFACE_TYPE

    __hash__ = None

    NONE = 0
    NODE = 1
    ELEMENT_EDGE = 2
    ELEMENT_FACE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ContactPairConstrainedSurfaceType.__setattr__ = __enum_setattr
ContactPairConstrainedSurfaceType.__delattr__ = __enum_delattr
