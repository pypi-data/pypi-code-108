'''_325.py

GearFlankRating
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating', 'GearFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GearFlankRating',)


class GearFlankRating(_0.APIBase):
    '''GearFlankRating

    This is a mastapy class.
    '''

    TYPE = _GEAR_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_contact_stress(self) -> 'float':
        '''float: 'MaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStress

    @property
    def maximum_static_contact_stress(self) -> 'float':
        '''float: 'MaximumStaticContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumStaticContactStress

    @property
    def maximum_bending_stress(self) -> 'float':
        '''float: 'MaximumBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumBendingStress

    @property
    def maximum_static_bending_stress(self) -> 'float':
        '''float: 'MaximumStaticBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumStaticBendingStress

    @property
    def reliability_bending(self) -> 'float':
        '''float: 'ReliabilityBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityBending

    @property
    def reliability_contact(self) -> 'float':
        '''float: 'ReliabilityContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReliabilityContact

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
    def bending_safety_factor_for_static(self) -> 'float':
        '''float: 'BendingSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingSafetyFactorForStatic

    @property
    def contact_safety_factor_for_static(self) -> 'float':
        '''float: 'ContactSafetyFactorForStatic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactSafetyFactorForStatic

    @property
    def cycles(self) -> 'float':
        '''float: 'Cycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Cycles

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
