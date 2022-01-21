'''_519.py

GleasonSpiralBevelGearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.bevel.standards import _521
from mastapy._internal.python_net import python_net_import

_GLEASON_SPIRAL_BEVEL_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel.Standards', 'GleasonSpiralBevelGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GleasonSpiralBevelGearSingleFlankRating',)


class GleasonSpiralBevelGearSingleFlankRating(_521.SpiralBevelGearSingleFlankRating):
    '''GleasonSpiralBevelGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _GLEASON_SPIRAL_BEVEL_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GleasonSpiralBevelGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def calculated_bending_stress(self) -> 'float':
        '''float: 'CalculatedBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedBendingStress

    @property
    def working_bending_stress(self) -> 'float':
        '''float: 'WorkingBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingBendingStress

    @property
    def calculated_contact_stress(self) -> 'float':
        '''float: 'CalculatedContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedContactStress

    @property
    def working_contact_stress(self) -> 'float':
        '''float: 'WorkingContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingContactStress

    @property
    def hardness_ratio_factor(self) -> 'float':
        '''float: 'HardnessRatioFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HardnessRatioFactor

    @property
    def calculated_scoring_index(self) -> 'float':
        '''float: 'CalculatedScoringIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedScoringIndex

    @property
    def gear_blank_temperature(self) -> 'float':
        '''float: 'GearBlankTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBlankTemperature

    @property
    def working_scoring_index(self) -> 'float':
        '''float: 'WorkingScoringIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingScoringIndex

    @property
    def contact_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'ContactSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactSafetyFactorForFatigue

    @property
    def bending_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'BendingSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingSafetyFactorForFatigue
