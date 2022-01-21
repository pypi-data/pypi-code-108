'''_1021.py

ReadonlyToothThicknessSpecification
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _1039
from mastapy._internal.python_net import python_net_import

_READONLY_TOOTH_THICKNESS_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ReadonlyToothThicknessSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('ReadonlyToothThicknessSpecification',)


class ReadonlyToothThicknessSpecification(_1039.ToothThicknessSpecification):
    '''ReadonlyToothThicknessSpecification

    This is a mastapy class.
    '''

    TYPE = _READONLY_TOOTH_THICKNESS_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ReadonlyToothThicknessSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def ball_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'BallDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.BallDiameter) if self.wrapped.BallDiameter is not None else None

    @ball_diameter.setter
    def ball_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.BallDiameter = value

    @property
    def number_of_teeth_for_chordal_span_test(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'NumberOfTeethForChordalSpanTest' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.NumberOfTeethForChordalSpanTest) if self.wrapped.NumberOfTeethForChordalSpanTest is not None else None

    @number_of_teeth_for_chordal_span_test.setter
    def number_of_teeth_for_chordal_span_test(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.NumberOfTeethForChordalSpanTest = value

    @property
    def diameter_at_thickness_measurement(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterAtThicknessMeasurement' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterAtThicknessMeasurement) if self.wrapped.DiameterAtThicknessMeasurement is not None else None

    @diameter_at_thickness_measurement.setter
    def diameter_at_thickness_measurement(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DiameterAtThicknessMeasurement = value
