'''_1942.py

TiltingPadThrustBearing
'''


from mastapy.bearings import _1656
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.bearings.bearing_designs.fluid_film import _1934
from mastapy._internal.python_net import python_net_import

_TILTING_PAD_THRUST_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm', 'TiltingPadThrustBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('TiltingPadThrustBearing',)


class TiltingPadThrustBearing(_1934.PadFluidFilmBearing):
    '''TiltingPadThrustBearing

    This is a mastapy class.
    '''

    TYPE = _TILTING_PAD_THRUST_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TiltingPadThrustBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tilting_pad_type(self) -> '_1656.TiltingPadTypes':
        '''TiltingPadTypes: 'TiltingPadType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TiltingPadType)
        return constructor.new(_1656.TiltingPadTypes)(value) if value is not None else None

    @tilting_pad_type.setter
    def tilting_pad_type(self, value: '_1656.TiltingPadTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TiltingPadType = value

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def pad_outer_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PadOuterDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PadOuterDiameter) if self.wrapped.PadOuterDiameter is not None else None

    @pad_outer_diameter.setter
    def pad_outer_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PadOuterDiameter = value

    @property
    def pad_inner_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PadInnerDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PadInnerDiameter) if self.wrapped.PadInnerDiameter is not None else None

    @pad_inner_diameter.setter
    def pad_inner_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PadInnerDiameter = value

    @property
    def pad_height(self) -> 'float':
        '''float: 'PadHeight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PadHeight

    @property
    def pad_circumferential_width(self) -> 'float':
        '''float: 'PadCircumferentialWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PadCircumferentialWidth

    @property
    def pad_width_aspect_ratio(self) -> 'float':
        '''float: 'PadWidthAspectRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PadWidthAspectRatio

    @property
    def pad_height_aspect_ratio(self) -> 'float':
        '''float: 'PadHeightAspectRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PadHeightAspectRatio

    @property
    def pivot_angular_offset(self) -> 'float':
        '''float: 'PivotAngularOffset' is the original name of this property.'''

        return self.wrapped.PivotAngularOffset

    @pivot_angular_offset.setter
    def pivot_angular_offset(self, value: 'float'):
        self.wrapped.PivotAngularOffset = float(value) if value else 0.0

    @property
    def non_dimensional_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NonDimensionalLoad' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NonDimensionalLoad) if self.wrapped.NonDimensionalLoad is not None else None

    @non_dimensional_load.setter
    def non_dimensional_load(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NonDimensionalLoad = value

    @property
    def non_dimensional_friction(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NonDimensionalFriction' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NonDimensionalFriction) if self.wrapped.NonDimensionalFriction is not None else None

    @non_dimensional_friction.setter
    def non_dimensional_friction(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NonDimensionalFriction = value

    @property
    def non_dimensional_inlet_flow(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NonDimensionalInletFlow' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NonDimensionalInletFlow) if self.wrapped.NonDimensionalInletFlow is not None else None

    @non_dimensional_inlet_flow.setter
    def non_dimensional_inlet_flow(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NonDimensionalInletFlow = value

    @property
    def non_dimensional_side_flow(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NonDimensionalSideFlow' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NonDimensionalSideFlow) if self.wrapped.NonDimensionalSideFlow is not None else None

    @non_dimensional_side_flow.setter
    def non_dimensional_side_flow(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NonDimensionalSideFlow = value

    @property
    def non_dimensional_minimum_film_thickness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NonDimensionalMinimumFilmThickness' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NonDimensionalMinimumFilmThickness) if self.wrapped.NonDimensionalMinimumFilmThickness is not None else None

    @non_dimensional_minimum_film_thickness.setter
    def non_dimensional_minimum_film_thickness(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NonDimensionalMinimumFilmThickness = value
