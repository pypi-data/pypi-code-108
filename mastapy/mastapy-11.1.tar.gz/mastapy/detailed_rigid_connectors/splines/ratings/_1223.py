'''_1223.py

AGMA6123SplineHalfRating
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines.ratings import _1231
from mastapy._internal.python_net import python_net_import

_AGMA6123_SPLINE_HALF_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.Ratings', 'AGMA6123SplineHalfRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA6123SplineHalfRating',)


class AGMA6123SplineHalfRating(_1231.SplineHalfRating):
    '''AGMA6123SplineHalfRating

    This is a mastapy class.
    '''

    TYPE = _AGMA6123_SPLINE_HALF_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA6123SplineHalfRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def allowable_stress_for_bursting(self) -> 'float':
        '''float: 'AllowableStressForBursting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressForBursting

    @property
    def allowable_stress_for_shearing(self) -> 'float':
        '''float: 'AllowableStressForShearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressForShearing

    @property
    def allowable_contact_stress(self) -> 'float':
        '''float: 'AllowableContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactStress

    @property
    def allowable_torque_for_wear_and_fretting(self) -> 'float':
        '''float: 'AllowableTorqueForWearAndFretting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTorqueForWearAndFretting

    @property
    def safety_factor_for_wear_and_fretting(self) -> 'float':
        '''float: 'SafetyFactorForWearAndFretting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForWearAndFretting

    @property
    def allowable_torque_for_shearing(self) -> 'float':
        '''float: 'AllowableTorqueForShearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTorqueForShearing

    @property
    def safety_factor_for_shearing(self) -> 'float':
        '''float: 'SafetyFactorForShearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForShearing

    @property
    def safety_factor_for_ring_bursting(self) -> 'float':
        '''float: 'SafetyFactorForRingBursting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForRingBursting
