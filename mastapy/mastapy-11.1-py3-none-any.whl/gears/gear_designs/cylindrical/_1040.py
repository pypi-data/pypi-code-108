'''_1040.py

ToothThicknessSpecificationBase
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _990
from mastapy.utility.units_and_measurements.measurements import _1452, _1468
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TOOTH_THICKNESS_SPECIFICATION_BASE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ToothThicknessSpecificationBase')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothThicknessSpecificationBase',)


class ToothThicknessSpecificationBase(_0.APIBase):
    '''ToothThicknessSpecificationBase

    This is a mastapy class.
    '''

    TYPE = _TOOTH_THICKNESS_SPECIFICATION_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothThicknessSpecificationBase.TYPE'):
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
    def ball_diameter_at_tip_form_diameter(self) -> 'float':
        '''float: 'BallDiameterAtTipFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BallDiameterAtTipFormDiameter

    @property
    def ball_diameter_at_form_diameter(self) -> 'float':
        '''float: 'BallDiameterAtFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BallDiameterAtFormDiameter

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
    def minimum_number_of_teeth_for_chordal_span_test(self) -> 'int':
        '''int: 'MinimumNumberOfTeethForChordalSpanTest' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumNumberOfTeethForChordalSpanTest

    @property
    def maximum_number_of_teeth_for_chordal_span_test(self) -> 'int':
        '''int: 'MaximumNumberOfTeethForChordalSpanTest' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNumberOfTeethForChordalSpanTest

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

    @property
    def normal_thickness(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'NormalThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.NormalThickness) if self.wrapped.NormalThickness is not None else None

    @property
    def normal_thickness_at_specified_diameter(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'NormalThicknessAtSpecifiedDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.NormalThicknessAtSpecifiedDiameter) if self.wrapped.NormalThicknessAtSpecifiedDiameter is not None else None

    @property
    def chordal_span(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'ChordalSpan' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.ChordalSpan) if self.wrapped.ChordalSpan is not None else None

    @property
    def over_balls(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'OverBalls' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.OverBalls) if self.wrapped.OverBalls is not None else None

    @property
    def transverse_thickness(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'TransverseThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.TransverseThickness) if self.wrapped.TransverseThickness is not None else None

    @property
    def transverse_thickness_at_specified_diameter(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'TransverseThicknessAtSpecifiedDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.TransverseThicknessAtSpecifiedDiameter) if self.wrapped.TransverseThicknessAtSpecifiedDiameter is not None else None

    @property
    def profile_shift_coefficient(self) -> '_990.CylindricalGearToothThicknessSpecification[_1468.Number]':
        '''CylindricalGearToothThicknessSpecification[Number]: 'ProfileShiftCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1468.Number](self.wrapped.ProfileShiftCoefficient) if self.wrapped.ProfileShiftCoefficient is not None else None

    @property
    def profile_shift(self) -> '_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]':
        '''CylindricalGearToothThicknessSpecification[LengthShort]: 'ProfileShift' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort](self.wrapped.ProfileShift) if self.wrapped.ProfileShift is not None else None

    @property
    def tooth_thickness(self) -> 'List[_990.CylindricalGearToothThicknessSpecification[_1452.LengthShort]]':
        '''List[CylindricalGearToothThicknessSpecification[LengthShort]]: 'ToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ToothThickness, constructor.new(_990.CylindricalGearToothThicknessSpecification)[_1452.LengthShort])
        return value
