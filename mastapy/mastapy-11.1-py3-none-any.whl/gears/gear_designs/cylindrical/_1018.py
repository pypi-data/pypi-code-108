'''_1018.py

Micropitting
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.gears import _304
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_MICROPITTING = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'Micropitting')


__docformat__ = 'restructuredtext en'
__all__ = ('Micropitting',)


class Micropitting(_1382.IndependentReportablePropertiesBase['Micropitting']):
    '''Micropitting

    This is a mastapy class.
    '''

    TYPE = _MICROPITTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Micropitting.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def estimate_bulk_temperature(self) -> 'bool':
        '''bool: 'EstimateBulkTemperature' is the original name of this property.'''

        return self.wrapped.EstimateBulkTemperature

    @estimate_bulk_temperature.setter
    def estimate_bulk_temperature(self, value: 'bool'):
        self.wrapped.EstimateBulkTemperature = bool(value) if value else False

    @property
    def method_a_coefficient_of_friction_method(self) -> 'enum_with_selected_value.EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod: 'MethodACoefficientOfFrictionMethod' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MethodACoefficientOfFrictionMethod, value) if self.wrapped.MethodACoefficientOfFrictionMethod is not None else None

    @method_a_coefficient_of_friction_method.setter
    def method_a_coefficient_of_friction_method(self, value: 'enum_with_selected_value.EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MethodACoefficientOfFrictionMethod = value
