'''_6531.py

AllRingPinsManufacturingError
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.bearings.tolerances import _1674
from mastapy.system_model.analyses_and_results.static_loads import _6660
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ALL_RING_PINS_MANUFACTURING_ERROR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'AllRingPinsManufacturingError')


__docformat__ = 'restructuredtext en'
__all__ = ('AllRingPinsManufacturingError',)


class AllRingPinsManufacturingError(_0.APIBase):
    '''AllRingPinsManufacturingError

    This is a mastapy class.
    '''

    TYPE = _ALL_RING_PINS_MANUFACTURING_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AllRingPinsManufacturingError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pin_diameter_error_for_all_pins(self) -> 'float':
        '''float: 'PinDiameterErrorForAllPins' is the original name of this property.'''

        return self.wrapped.PinDiameterErrorForAllPins

    @pin_diameter_error_for_all_pins.setter
    def pin_diameter_error_for_all_pins(self, value: 'float'):
        self.wrapped.PinDiameterErrorForAllPins = float(value) if value else 0.0

    @property
    def radial_position_error_for_all_pins(self) -> 'float':
        '''float: 'RadialPositionErrorForAllPins' is the original name of this property.'''

        return self.wrapped.RadialPositionErrorForAllPins

    @radial_position_error_for_all_pins.setter
    def radial_position_error_for_all_pins(self, value: 'float'):
        self.wrapped.RadialPositionErrorForAllPins = float(value) if value else 0.0

    @property
    def angular_position_error_for_all_pins(self) -> 'float':
        '''float: 'AngularPositionErrorForAllPins' is the original name of this property.'''

        return self.wrapped.AngularPositionErrorForAllPins

    @angular_position_error_for_all_pins.setter
    def angular_position_error_for_all_pins(self, value: 'float'):
        self.wrapped.AngularPositionErrorForAllPins = float(value) if value else 0.0

    @property
    def all_pins_roundness_chart(self) -> 'Image':
        '''Image: 'AllPinsRoundnessChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.AllPinsRoundnessChart)
        return value

    @property
    def roundness_specification(self) -> '_1674.RoundnessSpecification':
        '''RoundnessSpecification: 'RoundnessSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1674.RoundnessSpecification)(self.wrapped.RoundnessSpecification) if self.wrapped.RoundnessSpecification is not None else None

    @property
    def ring_pin_manufacturing_errors(self) -> 'List[_6660.RingPinManufacturingError]':
        '''List[RingPinManufacturingError]: 'RingPinManufacturingErrors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RingPinManufacturingErrors, constructor.new(_6660.RingPinManufacturingError))
        return value
