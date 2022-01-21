'''_1224.py

AGMA6123SplineJointRating
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines.ratings import _1232
from mastapy._internal.python_net import python_net_import

_AGMA6123_SPLINE_JOINT_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.Ratings', 'AGMA6123SplineJointRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA6123SplineJointRating',)


class AGMA6123SplineJointRating(_1232.SplineJointRating):
    '''AGMA6123SplineJointRating

    This is a mastapy class.
    '''

    TYPE = _AGMA6123_SPLINE_JOINT_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA6123SplineJointRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def load_distribution_factor(self) -> 'float':
        '''float: 'LoadDistributionFactor' is the original name of this property.'''

        return self.wrapped.LoadDistributionFactor

    @load_distribution_factor.setter
    def load_distribution_factor(self, value: 'float'):
        self.wrapped.LoadDistributionFactor = float(value) if value else 0.0

    @property
    def bursting_stress(self) -> 'float':
        '''float: 'BurstingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BurstingStress

    @property
    def tensile_tooth_bending_stress(self) -> 'float':
        '''float: 'TensileToothBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TensileToothBendingStress

    @property
    def centrifugal_hoop_stress(self) -> 'float':
        '''float: 'CentrifugalHoopStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CentrifugalHoopStress

    @property
    def total_tensile_stress(self) -> 'float':
        '''float: 'TotalTensileStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalTensileStress

    @property
    def allowable_ring_bursting_stress(self) -> 'float':
        '''float: 'AllowableRingBurstingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableRingBurstingStress

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
    def allowable_torque_for_torsional_failure(self) -> 'float':
        '''float: 'AllowableTorqueForTorsionalFailure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTorqueForTorsionalFailure

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

    @property
    def allowable_torque_for_wear_and_fretting(self) -> 'float':
        '''float: 'AllowableTorqueForWearAndFretting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableTorqueForWearAndFretting
