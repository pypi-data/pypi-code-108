'''_1232.py

SplineJointRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.detailed_rigid_connectors.splines.ratings import _1231
from mastapy.detailed_rigid_connectors.rating import _1236
from mastapy._internal.python_net import python_net_import

_SPLINE_JOINT_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.Ratings', 'SplineJointRating')


__docformat__ = 'restructuredtext en'
__all__ = ('SplineJointRating',)


class SplineJointRating(_1236.ShaftHubConnectionRating):
    '''SplineJointRating

    This is a mastapy class.
    '''

    TYPE = _SPLINE_JOINT_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SplineJointRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def dudley_maximum_effective_length(self) -> 'float':
        '''float: 'DudleyMaximumEffectiveLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DudleyMaximumEffectiveLength

    @property
    def radial_load(self) -> 'float':
        '''float: 'RadialLoad' is the original name of this property.'''

        return self.wrapped.RadialLoad

    @radial_load.setter
    def radial_load(self, value: 'float'):
        self.wrapped.RadialLoad = float(value) if value else 0.0

    @property
    def moment(self) -> 'float':
        '''float: 'Moment' is the original name of this property.'''

        return self.wrapped.Moment

    @moment.setter
    def moment(self, value: 'float'):
        self.wrapped.Moment = float(value) if value else 0.0

    @property
    def torque(self) -> 'float':
        '''float: 'Torque' is the original name of this property.'''

        return self.wrapped.Torque

    @torque.setter
    def torque(self, value: 'float'):
        self.wrapped.Torque = float(value) if value else 0.0

    @property
    def angular_velocity(self) -> 'float':
        '''float: 'AngularVelocity' is the original name of this property.'''

        return self.wrapped.AngularVelocity

    @angular_velocity.setter
    def angular_velocity(self, value: 'float'):
        self.wrapped.AngularVelocity = float(value) if value else 0.0

    @property
    def axial_force(self) -> 'float':
        '''float: 'AxialForce' is the original name of this property.'''

        return self.wrapped.AxialForce

    @axial_force.setter
    def axial_force(self, value: 'float'):
        self.wrapped.AxialForce = float(value) if value else 0.0

    @property
    def number_of_cycles(self) -> 'float':
        '''float: 'NumberOfCycles' is the original name of this property.'''

        return self.wrapped.NumberOfCycles

    @number_of_cycles.setter
    def number_of_cycles(self, value: 'float'):
        self.wrapped.NumberOfCycles = float(value) if value else 0.0

    @property
    def load(self) -> 'float':
        '''float: 'Load' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Load

    @property
    def allowable_bending_stress(self) -> 'float':
        '''float: 'AllowableBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBendingStress

    @property
    def allowable_contact_stress(self) -> 'float':
        '''float: 'AllowableContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactStress

    @property
    def allowable_compressive_stress(self) -> 'float':
        '''float: 'AllowableCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableCompressiveStress

    @property
    def allowable_shear_stress(self) -> 'float':
        '''float: 'AllowableShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableShearStress

    @property
    def allowable_bursting_stress(self) -> 'float':
        '''float: 'AllowableBurstingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBurstingStress

    @property
    def spline_half_ratings(self) -> 'List[_1231.SplineHalfRating]':
        '''List[SplineHalfRating]: 'SplineHalfRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SplineHalfRatings, constructor.new(_1231.SplineHalfRating))
        return value
