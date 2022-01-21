'''_52.py

CylindricalMisalignmentCalculator
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MISALIGNMENT_CALCULATOR = python_net_import('SMT.MastaAPI.NodalAnalysis', 'CylindricalMisalignmentCalculator')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMisalignmentCalculator',)


class CylindricalMisalignmentCalculator(_0.APIBase):
    '''CylindricalMisalignmentCalculator

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MISALIGNMENT_CALCULATOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMisalignmentCalculator.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_a_single_node_misalignment_due_to_tilt(self) -> 'float':
        '''float: 'GearASingleNodeMisalignmentDueToTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearASingleNodeMisalignmentDueToTilt

    @property
    def gear_a_single_node_misalignment_angle_due_to_tilt(self) -> 'float':
        '''float: 'GearASingleNodeMisalignmentAngleDueToTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearASingleNodeMisalignmentAngleDueToTilt

    @property
    def gear_a_single_node_misalignment_due_to_twist(self) -> 'float':
        '''float: 'GearASingleNodeMisalignmentDueToTwist' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearASingleNodeMisalignmentDueToTwist

    @property
    def gear_b_single_node_misalignment_due_to_tilt(self) -> 'float':
        '''float: 'GearBSingleNodeMisalignmentDueToTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBSingleNodeMisalignmentDueToTilt

    @property
    def gear_b_single_node_misalignment_angle_due_to_tilt(self) -> 'float':
        '''float: 'GearBSingleNodeMisalignmentAngleDueToTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBSingleNodeMisalignmentAngleDueToTilt

    @property
    def gear_b_single_node_misalignment_due_to_twist(self) -> 'float':
        '''float: 'GearBSingleNodeMisalignmentDueToTwist' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBSingleNodeMisalignmentDueToTwist

    @property
    def total_single_node_misalignment_due_to_tilt(self) -> 'float':
        '''float: 'TotalSingleNodeMisalignmentDueToTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalSingleNodeMisalignmentDueToTilt

    @property
    def total_single_node_misalignment_angle_due_to_tilt(self) -> 'float':
        '''float: 'TotalSingleNodeMisalignmentAngleDueToTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalSingleNodeMisalignmentAngleDueToTilt

    @property
    def total_single_node_misalignment_due_to_twist(self) -> 'float':
        '''float: 'TotalSingleNodeMisalignmentDueToTwist' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalSingleNodeMisalignmentDueToTwist

    @property
    def total_single_node_misalignment(self) -> 'float':
        '''float: 'TotalSingleNodeMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalSingleNodeMisalignment

    @property
    def gear_a_equivalent_misalignment_for_rating(self) -> 'float':
        '''float: 'GearAEquivalentMisalignmentForRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearAEquivalentMisalignmentForRating

    @property
    def gear_b_equivalent_misalignment_for_rating(self) -> 'float':
        '''float: 'GearBEquivalentMisalignmentForRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBEquivalentMisalignmentForRating

    @property
    def total_equivalent_misalignment_for_rating(self) -> 'float':
        '''float: 'TotalEquivalentMisalignmentForRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalEquivalentMisalignmentForRating

    @property
    def gear_a_line_fit_misalignment(self) -> 'float':
        '''float: 'GearALineFitMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearALineFitMisalignment

    @property
    def gear_b_line_fit_misalignment(self) -> 'float':
        '''float: 'GearBLineFitMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBLineFitMisalignment

    @property
    def total_line_fit_misalignment(self) -> 'float':
        '''float: 'TotalLineFitMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalLineFitMisalignment

    @property
    def gear_a_line_fit_misalignment_angle(self) -> 'float':
        '''float: 'GearALineFitMisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearALineFitMisalignmentAngle

    @property
    def gear_b_line_fit_misalignment_angle(self) -> 'float':
        '''float: 'GearBLineFitMisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBLineFitMisalignmentAngle

    @property
    def total_line_fit_misalignment_angle(self) -> 'float':
        '''float: 'TotalLineFitMisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalLineFitMisalignmentAngle

    @property
    def gear_a_rigid_body_misalignment(self) -> 'float':
        '''float: 'GearARigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearARigidBodyMisalignment

    @property
    def gear_a_radial_angular_component_of_rigid_body_misalignment(self) -> 'float':
        '''float: 'GearARadialAngularComponentOfRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearARadialAngularComponentOfRigidBodyMisalignment

    @property
    def gear_a_tangential_angular_component_of_rigid_body_misalignment(self) -> 'float':
        '''float: 'GearATangentialAngularComponentOfRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearATangentialAngularComponentOfRigidBodyMisalignment

    @property
    def gear_b_rigid_body_misalignment(self) -> 'float':
        '''float: 'GearBRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBRigidBodyMisalignment

    @property
    def gear_b_radial_angular_component_of_rigid_body_misalignment(self) -> 'float':
        '''float: 'GearBRadialAngularComponentOfRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBRadialAngularComponentOfRigidBodyMisalignment

    @property
    def gear_b_tangential_angular_component_of_rigid_body_misalignment(self) -> 'float':
        '''float: 'GearBTangentialAngularComponentOfRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBTangentialAngularComponentOfRigidBodyMisalignment

    @property
    def total_rigid_body_misalignment(self) -> 'float':
        '''float: 'TotalRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalRigidBodyMisalignment

    @property
    def total_radial_angular_component_of_rigid_body_misalignment(self) -> 'float':
        '''float: 'TotalRadialAngularComponentOfRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalRadialAngularComponentOfRigidBodyMisalignment

    @property
    def total_tangential_angular_component_of_rigid_body_misalignment(self) -> 'float':
        '''float: 'TotalTangentialAngularComponentOfRigidBodyMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalTangentialAngularComponentOfRigidBodyMisalignment

    @property
    def gear_a_rigid_body_misalignment_angle(self) -> 'float':
        '''float: 'GearARigidBodyMisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearARigidBodyMisalignmentAngle

    @property
    def gear_b_rigid_body_misalignment_angle(self) -> 'float':
        '''float: 'GearBRigidBodyMisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBRigidBodyMisalignmentAngle

    @property
    def total_rigid_body_misalignment_angle(self) -> 'float':
        '''float: 'TotalRigidBodyMisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalRigidBodyMisalignmentAngle

    @property
    def gear_a_transverse_separations(self) -> 'List[float]':
        '''List[float]: 'GearATransverseSeparations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.GearATransverseSeparations)
        return value

    @property
    def gear_b_transverse_separations(self) -> 'List[float]':
        '''List[float]: 'GearBTransverseSeparations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.GearBTransverseSeparations)
        return value

    @property
    def rigid_body_coordinate_system_x_axis(self) -> 'Vector3D':
        '''Vector3D: 'RigidBodyCoordinateSystemXAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.RigidBodyCoordinateSystemXAxis)
        return value

    @property
    def rigid_body_coordinate_system_y_axis(self) -> 'Vector3D':
        '''Vector3D: 'RigidBodyCoordinateSystemYAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.RigidBodyCoordinateSystemYAxis)
        return value
