'''_1242.py

KeywayRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.detailed_rigid_connectors.keyed_joints import _1237
from mastapy.detailed_rigid_connectors.keyed_joints.rating import _1241
from mastapy.detailed_rigid_connectors.interference_fits.rating import _1249
from mastapy._internal.python_net import python_net_import

_KEYWAY_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.KeyedJoints.Rating', 'KeywayRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KeywayRating',)


class KeywayRating(_1249.InterferenceFitRating):
    '''KeywayRating

    This is a mastapy class.
    '''

    TYPE = _KEYWAY_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KeywayRating.TYPE'):
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
    def circumferential_force(self) -> 'float':
        '''float: 'CircumferentialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CircumferentialForce

    @property
    def rated_force(self) -> 'float':
        '''float: 'RatedForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatedForce

    @property
    def extreme_force(self) -> 'float':
        '''float: 'ExtremeForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExtremeForce

    @property
    def rated_load_carrying_factor(self) -> 'float':
        '''float: 'RatedLoadCarryingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatedLoadCarryingFactor

    @property
    def extreme_load_carrying_factor(self) -> 'float':
        '''float: 'ExtremeLoadCarryingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExtremeLoadCarryingFactor

    @property
    def application_factor(self) -> 'float':
        '''float: 'ApplicationFactor' is the original name of this property.'''

        return self.wrapped.ApplicationFactor

    @application_factor.setter
    def application_factor(self, value: 'float'):
        self.wrapped.ApplicationFactor = float(value) if value else 0.0

    @property
    def load_distribution_factor_single_key(self) -> 'float':
        '''float: 'LoadDistributionFactorSingleKey' is the original name of this property.'''

        return self.wrapped.LoadDistributionFactorSingleKey

    @load_distribution_factor_single_key.setter
    def load_distribution_factor_single_key(self, value: 'float'):
        self.wrapped.LoadDistributionFactorSingleKey = float(value) if value else 0.0

    @property
    def load_distribution_factor(self) -> 'float':
        '''float: 'LoadDistributionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactor

    @property
    def frictional_engagement_factor_rated_load(self) -> 'float':
        '''float: 'FrictionalEngagementFactorRatedLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionalEngagementFactorRatedLoad

    @property
    def frictional_engagement_factor_extreme_load(self) -> 'float':
        '''float: 'FrictionalEngagementFactorExtremeLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionalEngagementFactorExtremeLoad

    @property
    def frictional_torque(self) -> 'float':
        '''float: 'FrictionalTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionalTorque

    @property
    def number_of_torque_reversals(self) -> 'float':
        '''float: 'NumberOfTorqueReversals' is the original name of this property.'''

        return self.wrapped.NumberOfTorqueReversals

    @number_of_torque_reversals.setter
    def number_of_torque_reversals(self, value: 'float'):
        self.wrapped.NumberOfTorqueReversals = float(value) if value else 0.0

    @property
    def torque_reversal_factor(self) -> 'float':
        '''float: 'TorqueReversalFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueReversalFactor

    @property
    def number_of_torque_peaks(self) -> 'float':
        '''float: 'NumberOfTorquePeaks' is the original name of this property.'''

        return self.wrapped.NumberOfTorquePeaks

    @number_of_torque_peaks.setter
    def number_of_torque_peaks(self, value: 'float'):
        self.wrapped.NumberOfTorquePeaks = float(value) if value else 0.0

    @property
    def torque_peak_factor(self) -> 'float':
        '''float: 'TorquePeakFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorquePeakFactor

    @property
    def inner_component_rated_safety_factor(self) -> 'float':
        '''float: 'InnerComponentRatedSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerComponentRatedSafetyFactor

    @property
    def outer_component_rated_safety_factor(self) -> 'float':
        '''float: 'OuterComponentRatedSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterComponentRatedSafetyFactor

    @property
    def key_rated_safety_factor(self) -> 'float':
        '''float: 'KeyRatedSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.KeyRatedSafetyFactor

    @property
    def inner_component_extreme_safety_factor(self) -> 'float':
        '''float: 'InnerComponentExtremeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerComponentExtremeSafetyFactor

    @property
    def outer_component_extreme_safety_factor(self) -> 'float':
        '''float: 'OuterComponentExtremeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterComponentExtremeSafetyFactor

    @property
    def key_extreme_safety_factor(self) -> 'float':
        '''float: 'KeyExtremeSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.KeyExtremeSafetyFactor

    @property
    def keyed_joint_design(self) -> '_1237.KeyedJointDesign':
        '''KeyedJointDesign: 'KeyedJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1237.KeyedJointDesign)(self.wrapped.KeyedJointDesign) if self.wrapped.KeyedJointDesign is not None else None

    @property
    def keyway_half_ratings(self) -> 'List[_1241.KeywayHalfRating]':
        '''List[KeywayHalfRating]: 'KeywayHalfRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KeywayHalfRatings, constructor.new(_1241.KeywayHalfRating))
        return value
