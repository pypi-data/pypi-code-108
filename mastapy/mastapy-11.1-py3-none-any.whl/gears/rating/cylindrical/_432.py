'''_432.py

CylindricalPlasticGearRatingSettings
'''


from mastapy._internal import constructor
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLASTIC_GEAR_RATING_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalPlasticGearRatingSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlasticGearRatingSettings',)


class CylindricalPlasticGearRatingSettings(_1387.PerMachineSettings):
    '''CylindricalPlasticGearRatingSettings

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLASTIC_GEAR_RATING_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlasticGearRatingSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_approximate_value_of_double_the_normal_module_for_profile_line_length_of_the_active_tooth_flank(self) -> 'bool':
        '''bool: 'UseApproximateValueOfDoubleTheNormalModuleForProfileLineLengthOfTheActiveToothFlank' is the original name of this property.'''

        return self.wrapped.UseApproximateValueOfDoubleTheNormalModuleForProfileLineLengthOfTheActiveToothFlank

    @use_approximate_value_of_double_the_normal_module_for_profile_line_length_of_the_active_tooth_flank.setter
    def use_approximate_value_of_double_the_normal_module_for_profile_line_length_of_the_active_tooth_flank(self, value: 'bool'):
        self.wrapped.UseApproximateValueOfDoubleTheNormalModuleForProfileLineLengthOfTheActiveToothFlank = bool(value) if value else False

    @property
    def use_approximate_value_of_10_for_spiral_helix_angle_factor_for_contact_rating(self) -> 'bool':
        '''bool: 'UseApproximateValueOf10ForSpiralHelixAngleFactorForContactRating' is the original name of this property.'''

        return self.wrapped.UseApproximateValueOf10ForSpiralHelixAngleFactorForContactRating

    @use_approximate_value_of_10_for_spiral_helix_angle_factor_for_contact_rating.setter
    def use_approximate_value_of_10_for_spiral_helix_angle_factor_for_contact_rating(self, value: 'bool'):
        self.wrapped.UseApproximateValueOf10ForSpiralHelixAngleFactorForContactRating = bool(value) if value else False
