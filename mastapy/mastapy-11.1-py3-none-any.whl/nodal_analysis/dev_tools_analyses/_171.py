'''_171.py

FESurfaceDrawingOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FE_SURFACE_DRAWING_OPTION = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FESurfaceDrawingOption')


__docformat__ = 'restructuredtext en'
__all__ = ('FESurfaceDrawingOption',)


class FESurfaceDrawingOption(Enum):
    '''FESurfaceDrawingOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FE_SURFACE_DRAWING_OPTION

    __hash__ = None

    NONE = 0
    TRANSPARENT = 1
    SOLID = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FESurfaceDrawingOption.__setattr__ = __enum_setattr
FESurfaceDrawingOption.__delattr__ = __enum_delattr
