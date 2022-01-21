'''_1234.py

GBT17855SplineJointDutyCycleRating
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GBT17855_SPLINE_JOINT_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.DutyCycleRatings', 'GBT17855SplineJointDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GBT17855SplineJointDutyCycleRating',)


class GBT17855SplineJointDutyCycleRating(_0.APIBase):
    '''GBT17855SplineJointDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _GBT17855_SPLINE_JOINT_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GBT17855SplineJointDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor_for_equivalent_stress(self) -> 'float':
        '''float: 'SafetyFactorForEquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForEquivalentStress

    @property
    def safety_factor_for_compressive_stress(self) -> 'float':
        '''float: 'SafetyFactorForCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForCompressiveStress

    @property
    def safety_factor_for_tooth_shearing_stress(self) -> 'float':
        '''float: 'SafetyFactorForToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForToothShearingStress

    @property
    def safety_factor_for_root_bending_stress(self) -> 'float':
        '''float: 'SafetyFactorForRootBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForRootBendingStress

    @property
    def safety_factor_for_wearing_stress(self) -> 'float':
        '''float: 'SafetyFactorForWearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForWearingStress
