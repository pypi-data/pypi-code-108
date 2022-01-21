'''_5209.py

ShaftAndHousingFlexibilityOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SHAFT_AND_HOUSING_FLEXIBILITY_OPTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'ShaftAndHousingFlexibilityOption')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftAndHousingFlexibilityOption',)


class ShaftAndHousingFlexibilityOption(Enum):
    '''ShaftAndHousingFlexibilityOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SHAFT_AND_HOUSING_FLEXIBILITY_OPTION

    __hash__ = None

    LOAD_CASE_SETTING = 0
    NONE_RIGID_BODY = 1
    FULL_FLEXIBILITIES = 2
    TORSIONAL_ONLY = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ShaftAndHousingFlexibilityOption.__setattr__ = __enum_setattr
ShaftAndHousingFlexibilityOption.__delattr__ = __enum_delattr
