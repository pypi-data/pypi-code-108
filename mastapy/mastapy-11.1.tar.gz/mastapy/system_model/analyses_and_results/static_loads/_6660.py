'''_6660.py

RingPinManufacturingError
'''


from PIL.Image import Image

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy.bearings.tolerances import _1674
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RING_PIN_MANUFACTURING_ERROR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'RingPinManufacturingError')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinManufacturingError',)


class RingPinManufacturingError(_0.APIBase):
    '''RingPinManufacturingError

    This is a mastapy class.
    '''

    TYPE = _RING_PIN_MANUFACTURING_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinManufacturingError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pin_diameter_error(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PinDiameterError' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PinDiameterError) if self.wrapped.PinDiameterError is not None else None

    @pin_diameter_error.setter
    def pin_diameter_error(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PinDiameterError = value

    @property
    def pin_radial_position_error(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PinRadialPositionError' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PinRadialPositionError) if self.wrapped.PinRadialPositionError is not None else None

    @pin_radial_position_error.setter
    def pin_radial_position_error(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PinRadialPositionError = value

    @property
    def pin_angular_position_error(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PinAngularPositionError' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PinAngularPositionError) if self.wrapped.PinAngularPositionError is not None else None

    @pin_angular_position_error.setter
    def pin_angular_position_error(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PinAngularPositionError = value

    @property
    def override_all_pins_roundness_specification(self) -> 'bool':
        '''bool: 'OverrideAllPinsRoundnessSpecification' is the original name of this property.'''

        return self.wrapped.OverrideAllPinsRoundnessSpecification

    @override_all_pins_roundness_specification.setter
    def override_all_pins_roundness_specification(self, value: 'bool'):
        self.wrapped.OverrideAllPinsRoundnessSpecification = bool(value) if value else False

    @property
    def show_pin_roundness_chart(self) -> 'bool':
        '''bool: 'ShowPinRoundnessChart' is the original name of this property.'''

        return self.wrapped.ShowPinRoundnessChart

    @show_pin_roundness_chart.setter
    def show_pin_roundness_chart(self, value: 'bool'):
        self.wrapped.ShowPinRoundnessChart = bool(value) if value else False

    @property
    def pin_roundness_chart(self) -> 'Image':
        '''Image: 'PinRoundnessChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.PinRoundnessChart)
        return value

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def roundness_specification(self) -> '_1674.RoundnessSpecification':
        '''RoundnessSpecification: 'RoundnessSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1674.RoundnessSpecification)(self.wrapped.RoundnessSpecification) if self.wrapped.RoundnessSpecification is not None else None
