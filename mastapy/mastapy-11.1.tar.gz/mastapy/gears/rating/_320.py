'''_320.py

AbstractGearRating
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1159
from mastapy._internal.python_net import python_net_import

_ABSTRACT_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating', 'AbstractGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractGearRating',)


class AbstractGearRating(_1159.AbstractGearAnalysis):
    '''AbstractGearRating

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def damage_bending(self) -> 'float':
        '''float: 'DamageBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageBending

    @property
    def damage_contact(self) -> 'float':
        '''float: 'DamageContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageContact

    @property
    def bending_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'BendingSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingSafetyFactorForFatigue

    @property
    def contact_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'ContactSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactSafetyFactorForFatigue

    @property
    def total_gear_reliability(self) -> 'float':
        '''float: 'TotalGearReliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalGearReliability

    @property
    def gear_reliability_bending(self) -> 'float':
        '''float: 'GearReliabilityBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearReliabilityBending

    @property
    def gear_reliability_contact(self) -> 'float':
        '''float: 'GearReliabilityContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearReliabilityContact

    @property
    def contact_safety_factor_for_static(self) -> 'float':
        '''float: 'ContactSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactSafetyFactorForStatic

    @property
    def bending_safety_factor_for_static(self) -> 'float':
        '''float: 'BendingSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingSafetyFactorForStatic

    @property
    def cycles_to_fail_bending(self) -> 'float':
        '''float: 'CyclesToFailBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CyclesToFailBending

    @property
    def cycles_to_fail_contact(self) -> 'float':
        '''float: 'CyclesToFailContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CyclesToFailContact

    @property
    def cycles_to_fail(self) -> 'float':
        '''float: 'CyclesToFail' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CyclesToFail

    @property
    def time_to_fail_bending(self) -> 'float':
        '''float: 'TimeToFailBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeToFailBending

    @property
    def time_to_fail_contact(self) -> 'float':
        '''float: 'TimeToFailContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeToFailContact

    @property
    def time_to_fail(self) -> 'float':
        '''float: 'TimeToFail' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeToFail

    @property
    def normalized_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForFatigue

    @property
    def normalized_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedSafetyFactorForStatic

    @property
    def normalized_bending_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedBendingSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedBendingSafetyFactorForFatigue

    @property
    def normalized_bending_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedBendingSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedBendingSafetyFactorForStatic

    @property
    def normalized_contact_safety_factor_for_fatigue(self) -> 'float':
        '''float: 'NormalizedContactSafetyFactorForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedContactSafetyFactorForFatigue

    @property
    def normalized_contact_safety_factor_for_static(self) -> 'float':
        '''float: 'NormalizedContactSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalizedContactSafetyFactorForStatic
