'''_408.py

GleasonHypoidGearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.conical import _503
from mastapy._internal.python_net import python_net_import

_GLEASON_HYPOID_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Hypoid.Standards', 'GleasonHypoidGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GleasonHypoidGearSingleFlankRating',)


class GleasonHypoidGearSingleFlankRating(_503.ConicalGearSingleFlankRating):
    '''GleasonHypoidGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _GLEASON_HYPOID_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GleasonHypoidGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def geometry_factor_j(self) -> 'float':
        '''float: 'GeometryFactorJ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorJ

    @property
    def calculated_bending_stress(self) -> 'float':
        '''float: 'CalculatedBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedBendingStress

    @property
    def life_factor_bending(self) -> 'float':
        '''float: 'LifeFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorBending

    @property
    def life_factor_contact(self) -> 'float':
        '''float: 'LifeFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorContact

    @property
    def working_bending_stress(self) -> 'float':
        '''float: 'WorkingBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingBendingStress

    @property
    def working_contact_stress(self) -> 'float':
        '''float: 'WorkingContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingContactStress

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
