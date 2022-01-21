'''_4857.py

CoordinateSystemForWhine
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COORDINATE_SYSTEM_FOR_WHINE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'CoordinateSystemForWhine')


__docformat__ = 'restructuredtext en'
__all__ = ('CoordinateSystemForWhine',)


class CoordinateSystemForWhine(Enum):
    '''CoordinateSystemForWhine

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COORDINATE_SYSTEM_FOR_WHINE

    __hash__ = None

    LOCAL_COORDINATE_SYSTEM = 0
    GLOBAL_COORDINATE_SYSTEM = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CoordinateSystemForWhine.__setattr__ = __enum_setattr
CoordinateSystemForWhine.__delattr__ = __enum_delattr
