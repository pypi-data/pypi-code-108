'''_5826.py

ModalContributionFilteringMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MODAL_CONTRIBUTION_FILTERING_METHOD = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Results', 'ModalContributionFilteringMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('ModalContributionFilteringMethod',)


class ModalContributionFilteringMethod(Enum):
    '''ModalContributionFilteringMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MODAL_CONTRIBUTION_FILTERING_METHOD

    __hash__ = None

    NO_FILTERING = 0
    ABSOLUTE_AT_MODE_NATURAL_FREQUENCY = 1
    ABSOLUTE_AT_FIXED_FREQUENCY = 2
    INTEGRAL_OVER_FREQUENCY_RANGE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ModalContributionFilteringMethod.__setattr__ = __enum_setattr
ModalContributionFilteringMethod.__delattr__ = __enum_delattr
