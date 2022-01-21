'''_493.py

DIN3990GearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _472
from mastapy._internal.python_net import python_net_import

_DIN3990_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.DIN3990', 'DIN3990GearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('DIN3990GearSingleFlankRating',)


class DIN3990GearSingleFlankRating(_472.ISO63361996GearSingleFlankRating):
    '''DIN3990GearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _DIN3990_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DIN3990GearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relative_notch_sensitivity_factor_for_static_stress(self) -> 'float':
        '''float: 'RelativeNotchSensitivityFactorForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeNotchSensitivityFactorForStaticStress
