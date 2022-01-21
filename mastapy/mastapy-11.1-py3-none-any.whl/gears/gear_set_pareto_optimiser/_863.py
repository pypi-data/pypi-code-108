'''_863.py

CandidateDisplayChoice
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CANDIDATE_DISPLAY_CHOICE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'CandidateDisplayChoice')


__docformat__ = 'restructuredtext en'
__all__ = ('CandidateDisplayChoice',)


class CandidateDisplayChoice(Enum):
    '''CandidateDisplayChoice

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CANDIDATE_DISPLAY_CHOICE

    __hash__ = None

    ALL_FEASIBLE_CANDIDATES = 0
    CANDIDATES_AFTER_FILTERING = 1
    DOMINANT_CANDIDATES = 2
    CANDIDATES_SELECTED_IN_CHART = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CandidateDisplayChoice.__setattr__ = __enum_setattr
CandidateDisplayChoice.__delattr__ = __enum_delattr
