'''_558.py

ISOTR1417912001CoefficientOfFrictionConstants
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS = python_net_import('SMT.MastaAPI.Gears.Materials', 'ISOTR1417912001CoefficientOfFrictionConstants')


__docformat__ = 'restructuredtext en'
__all__ = ('ISOTR1417912001CoefficientOfFrictionConstants',)


class ISOTR1417912001CoefficientOfFrictionConstants(_1597.NamedDatabaseItem):
    '''ISOTR1417912001CoefficientOfFrictionConstants

    This is a mastapy class.
    '''

    TYPE = _ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISOTR1417912001CoefficientOfFrictionConstants.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def constant_c1(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ConstantC1' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ConstantC1) if self.wrapped.ConstantC1 is not None else None

    @constant_c1.setter
    def constant_c1(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ConstantC1 = value

    @property
    def oil_viscosity_exponent(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OilViscosityExponent' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OilViscosityExponent) if self.wrapped.OilViscosityExponent is not None else None

    @oil_viscosity_exponent.setter
    def oil_viscosity_exponent(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OilViscosityExponent = value

    @property
    def load_intensity_exponent(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LoadIntensityExponent' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LoadIntensityExponent) if self.wrapped.LoadIntensityExponent is not None else None

    @load_intensity_exponent.setter
    def load_intensity_exponent(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LoadIntensityExponent = value

    @property
    def pitch_line_velocity_exponent(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PitchLineVelocityExponent' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PitchLineVelocityExponent) if self.wrapped.PitchLineVelocityExponent is not None else None

    @pitch_line_velocity_exponent.setter
    def pitch_line_velocity_exponent(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PitchLineVelocityExponent = value
