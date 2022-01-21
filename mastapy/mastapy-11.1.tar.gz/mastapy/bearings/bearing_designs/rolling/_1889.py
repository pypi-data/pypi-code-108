'''_1889.py

BallBearing
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_designs.rolling import _1890, _1912
from mastapy._internal.python_net import python_net_import

_BALL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'BallBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('BallBearing',)


class BallBearing(_1912.RollingBearing):
    '''BallBearing

    This is a mastapy class.
    '''

    TYPE = _BALL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BallBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def element_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementDiameter) if self.wrapped.ElementDiameter is not None else None

    @element_diameter.setter
    def element_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementDiameter = value

    @property
    def inner_race_osculation(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRaceOsculation' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRaceOsculation) if self.wrapped.InnerRaceOsculation is not None else None

    @inner_race_osculation.setter
    def inner_race_osculation(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRaceOsculation = value

    @property
    def inner_groove_radius_as_percentage_of_element_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerGrooveRadiusAsPercentageOfElementDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerGrooveRadiusAsPercentageOfElementDiameter) if self.wrapped.InnerGrooveRadiusAsPercentageOfElementDiameter is not None else None

    @inner_groove_radius_as_percentage_of_element_diameter.setter
    def inner_groove_radius_as_percentage_of_element_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerGrooveRadiusAsPercentageOfElementDiameter = value

    @property
    def inner_groove_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerGrooveRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerGrooveRadius) if self.wrapped.InnerGrooveRadius is not None else None

    @inner_groove_radius.setter
    def inner_groove_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerGrooveRadius = value

    @property
    def outer_race_osculation(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRaceOsculation' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRaceOsculation) if self.wrapped.OuterRaceOsculation is not None else None

    @outer_race_osculation.setter
    def outer_race_osculation(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRaceOsculation = value

    @property
    def outer_groove_radius_as_percentage_of_element_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterGrooveRadiusAsPercentageOfElementDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterGrooveRadiusAsPercentageOfElementDiameter) if self.wrapped.OuterGrooveRadiusAsPercentageOfElementDiameter is not None else None

    @outer_groove_radius_as_percentage_of_element_diameter.setter
    def outer_groove_radius_as_percentage_of_element_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterGrooveRadiusAsPercentageOfElementDiameter = value

    @property
    def outer_groove_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterGrooveRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterGrooveRadius) if self.wrapped.OuterGrooveRadius is not None else None

    @outer_groove_radius.setter
    def outer_groove_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterGrooveRadius = value

    @property
    def inner_ring_left_shoulder_height(self) -> 'float':
        '''float: 'InnerRingLeftShoulderHeight' is the original name of this property.'''

        return self.wrapped.InnerRingLeftShoulderHeight

    @inner_ring_left_shoulder_height.setter
    def inner_ring_left_shoulder_height(self, value: 'float'):
        self.wrapped.InnerRingLeftShoulderHeight = float(value) if value else 0.0

    @property
    def inner_ring_right_shoulder_height(self) -> 'float':
        '''float: 'InnerRingRightShoulderHeight' is the original name of this property.'''

        return self.wrapped.InnerRingRightShoulderHeight

    @inner_ring_right_shoulder_height.setter
    def inner_ring_right_shoulder_height(self, value: 'float'):
        self.wrapped.InnerRingRightShoulderHeight = float(value) if value else 0.0

    @property
    def outer_ring_left_shoulder_height(self) -> 'float':
        '''float: 'OuterRingLeftShoulderHeight' is the original name of this property.'''

        return self.wrapped.OuterRingLeftShoulderHeight

    @outer_ring_left_shoulder_height.setter
    def outer_ring_left_shoulder_height(self, value: 'float'):
        self.wrapped.OuterRingLeftShoulderHeight = float(value) if value else 0.0

    @property
    def outer_ring_right_shoulder_height(self) -> 'float':
        '''float: 'OuterRingRightShoulderHeight' is the original name of this property.'''

        return self.wrapped.OuterRingRightShoulderHeight

    @outer_ring_right_shoulder_height.setter
    def outer_ring_right_shoulder_height(self, value: 'float'):
        self.wrapped.OuterRingRightShoulderHeight = float(value) if value else 0.0

    @property
    def inner_left_shoulder_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerLeftShoulderDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerLeftShoulderDiameter) if self.wrapped.InnerLeftShoulderDiameter is not None else None

    @inner_left_shoulder_diameter.setter
    def inner_left_shoulder_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerLeftShoulderDiameter = value

    @property
    def inner_right_shoulder_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRightShoulderDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRightShoulderDiameter) if self.wrapped.InnerRightShoulderDiameter is not None else None

    @inner_right_shoulder_diameter.setter
    def inner_right_shoulder_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRightShoulderDiameter = value

    @property
    def outer_left_shoulder_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterLeftShoulderDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterLeftShoulderDiameter) if self.wrapped.OuterLeftShoulderDiameter is not None else None

    @outer_left_shoulder_diameter.setter
    def outer_left_shoulder_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterLeftShoulderDiameter = value

    @property
    def outer_right_shoulder_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRightShoulderDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRightShoulderDiameter) if self.wrapped.OuterRightShoulderDiameter is not None else None

    @outer_right_shoulder_diameter.setter
    def outer_right_shoulder_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRightShoulderDiameter = value

    @property
    def inner_ring_shoulder_chamfer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRingShoulderChamfer' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRingShoulderChamfer) if self.wrapped.InnerRingShoulderChamfer is not None else None

    @inner_ring_shoulder_chamfer.setter
    def inner_ring_shoulder_chamfer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRingShoulderChamfer = value

    @property
    def outer_ring_shoulder_chamfer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRingShoulderChamfer' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRingShoulderChamfer) if self.wrapped.OuterRingShoulderChamfer is not None else None

    @outer_ring_shoulder_chamfer.setter
    def outer_ring_shoulder_chamfer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRingShoulderChamfer = value

    @property
    def contact_radius_at_right_angle_to_rolling_direction_inner(self) -> 'float':
        '''float: 'ContactRadiusAtRightAngleToRollingDirectionInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRadiusAtRightAngleToRollingDirectionInner

    @property
    def contact_radius_at_right_angle_to_rolling_direction_outer(self) -> 'float':
        '''float: 'ContactRadiusAtRightAngleToRollingDirectionOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRadiusAtRightAngleToRollingDirectionOuter

    @property
    def relative_curvature_difference_outer(self) -> 'float':
        '''float: 'RelativeCurvatureDifferenceOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeCurvatureDifferenceOuter

    @property
    def relative_curvature_difference_inner(self) -> 'float':
        '''float: 'RelativeCurvatureDifferenceInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeCurvatureDifferenceInner

    @property
    def curvature_sum_inner(self) -> 'float':
        '''float: 'CurvatureSumInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurvatureSumInner

    @property
    def curvature_sum_outer(self) -> 'float':
        '''float: 'CurvatureSumOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurvatureSumOuter

    @property
    def coefficient_of_friction_between_inner_race_and_element(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CoefficientOfFrictionBetweenInnerRaceAndElement' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CoefficientOfFrictionBetweenInnerRaceAndElement) if self.wrapped.CoefficientOfFrictionBetweenInnerRaceAndElement is not None else None

    @coefficient_of_friction_between_inner_race_and_element.setter
    def coefficient_of_friction_between_inner_race_and_element(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CoefficientOfFrictionBetweenInnerRaceAndElement = value

    @property
    def coefficient_of_friction_between_outer_race_and_element(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CoefficientOfFrictionBetweenOuterRaceAndElement' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CoefficientOfFrictionBetweenOuterRaceAndElement) if self.wrapped.CoefficientOfFrictionBetweenOuterRaceAndElement is not None else None

    @coefficient_of_friction_between_outer_race_and_element.setter
    def coefficient_of_friction_between_outer_race_and_element(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CoefficientOfFrictionBetweenOuterRaceAndElement = value

    @property
    def shoulders(self) -> 'List[_1890.BallBearingShoulderDefinition]':
        '''List[BallBearingShoulderDefinition]: 'Shoulders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Shoulders, constructor.new(_1890.BallBearingShoulderDefinition))
        return value
