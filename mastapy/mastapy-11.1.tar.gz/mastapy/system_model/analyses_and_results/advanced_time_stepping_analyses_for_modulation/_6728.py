'''_6728.py

AtsamExcitationsOrOthers
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ATSAM_EXCITATIONS_OR_OTHERS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'AtsamExcitationsOrOthers')


__docformat__ = 'restructuredtext en'
__all__ = ('AtsamExcitationsOrOthers',)


class AtsamExcitationsOrOthers(Enum):
    '''AtsamExcitationsOrOthers

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ATSAM_EXCITATIONS_OR_OTHERS

    __hash__ = None

    ADVANCED_MODEL = 0
    OTHER_EXCITATIONS = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AtsamExcitationsOrOthers.__setattr__ = __enum_setattr
AtsamExcitationsOrOthers.__delattr__ = __enum_delattr
