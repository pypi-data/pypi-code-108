'''_1920.py

ThrustBallBearing
'''


from mastapy.bearings import _1646
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.bearings.bearing_designs.rolling import _1889
from mastapy._internal.python_net import python_net_import

_THRUST_BALL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'ThrustBallBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('ThrustBallBearing',)


class ThrustBallBearing(_1889.BallBearing):
    '''ThrustBallBearing

    This is a mastapy class.
    '''

    TYPE = _THRUST_BALL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ThrustBallBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def outer_ring_mounting(self) -> '_1646.OuterRingMounting':
        '''OuterRingMounting: 'OuterRingMounting' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.OuterRingMounting)
        return constructor.new(_1646.OuterRingMounting)(value) if value is not None else None

    @outer_ring_mounting.setter
    def outer_ring_mounting(self, value: '_1646.OuterRingMounting'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.OuterRingMounting = value

    @property
    def center_ring_corner_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CenterRingCornerRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CenterRingCornerRadius) if self.wrapped.CenterRingCornerRadius is not None else None

    @center_ring_corner_radius.setter
    def center_ring_corner_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CenterRingCornerRadius = value

    @property
    def sum_of_the_centre_and_inner_ring_left_corner_radius(self) -> 'float':
        '''float: 'SumOfTheCentreAndInnerRingLeftCornerRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumOfTheCentreAndInnerRingLeftCornerRadius

    @property
    def sum_of_the_centre_and_inner_ring_right_corner_radius(self) -> 'float':
        '''float: 'SumOfTheCentreAndInnerRingRightCornerRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SumOfTheCentreAndInnerRingRightCornerRadius

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def outer_ring_inner_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRingInnerDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRingInnerDiameter) if self.wrapped.OuterRingInnerDiameter is not None else None

    @outer_ring_inner_diameter.setter
    def outer_ring_inner_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRingInnerDiameter = value

    @property
    def inner_ring_outer_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRingOuterDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRingOuterDiameter) if self.wrapped.InnerRingOuterDiameter is not None else None

    @inner_ring_outer_diameter.setter
    def inner_ring_outer_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRingOuterDiameter = value

    @property
    def sphered_seat_offset(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SpheredSeatOffset' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SpheredSeatOffset) if self.wrapped.SpheredSeatOffset is not None else None

    @sphered_seat_offset.setter
    def sphered_seat_offset(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SpheredSeatOffset = value

    @property
    def sphered_seat_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SpheredSeatRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SpheredSeatRadius) if self.wrapped.SpheredSeatRadius is not None else None

    @sphered_seat_radius.setter
    def sphered_seat_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SpheredSeatRadius = value
