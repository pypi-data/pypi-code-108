'''_7067.py

UseLtcaInAsdOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_USE_LTCA_IN_ASD_OPTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'UseLtcaInAsdOption')


__docformat__ = 'restructuredtext en'
__all__ = ('UseLtcaInAsdOption',)


class UseLtcaInAsdOption(Enum):
    '''UseLtcaInAsdOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _USE_LTCA_IN_ASD_OPTION

    __hash__ = None

    NO = 0
    YES = 1
    AUTO = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


UseLtcaInAsdOption.__setattr__ = __enum_setattr
UseLtcaInAsdOption.__delattr__ = __enum_delattr
