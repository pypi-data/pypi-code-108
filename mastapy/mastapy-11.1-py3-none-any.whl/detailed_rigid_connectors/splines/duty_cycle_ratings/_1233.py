'''_1233.py

AGMA6123SplineJointDutyCycleRating
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_AGMA6123_SPLINE_JOINT_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.DutyCycleRatings', 'AGMA6123SplineJointDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA6123SplineJointDutyCycleRating',)


class AGMA6123SplineJointDutyCycleRating(_0.APIBase):
    '''AGMA6123SplineJointDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _AGMA6123_SPLINE_JOINT_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA6123SplineJointDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor_for_torsional_failure(self) -> 'float':
        '''float: 'SafetyFactorForTorsionalFailure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForTorsionalFailure

    @property
    def safety_factor_for_wear_and_fretting(self) -> 'float':
        '''float: 'SafetyFactorForWearAndFretting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForWearAndFretting

    @property
    def safety_factor_for_ring_bursting(self) -> 'float':
        '''float: 'SafetyFactorForRingBursting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForRingBursting

    @property
    def safety_factor_for_shearing(self) -> 'float':
        '''float: 'SafetyFactorForShearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForShearing
