'''_6523.py

AbstractShaftOrHousingLoadCase
'''


from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5209
from mastapy.system_model.part_model import _2179, _2178, _2194
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.cycloidal import _2309
from mastapy.system_model.analyses_and_results.static_loads import _6551
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'AbstractShaftOrHousingLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingLoadCase',)


class AbstractShaftOrHousingLoadCase(_6551.ComponentLoadCase):
    '''AbstractShaftOrHousingLoadCase

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rayleigh_damping_alpha(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RayleighDampingAlpha' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RayleighDampingAlpha) if self.wrapped.RayleighDampingAlpha is not None else None

    @rayleigh_damping_alpha.setter
    def rayleigh_damping_alpha(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RayleighDampingAlpha = value

    @property
    def include_flexibilities_setting(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ShaftAndHousingFlexibilityOption':
        '''enum_with_selected_value.EnumWithSelectedValue_ShaftAndHousingFlexibilityOption: 'IncludeFlexibilitiesSetting' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ShaftAndHousingFlexibilityOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.IncludeFlexibilitiesSetting, value) if self.wrapped.IncludeFlexibilitiesSetting is not None else None

    @include_flexibilities_setting.setter
    def include_flexibilities_setting(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ShaftAndHousingFlexibilityOption.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ShaftAndHousingFlexibilityOption.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.IncludeFlexibilitiesSetting = value

    @property
    def temperature(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Temperature' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Temperature) if self.wrapped.Temperature is not None else None

    @temperature.setter
    def temperature(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Temperature = value

    @property
    def component_design(self) -> '_2179.AbstractShaftOrHousing':
        '''AbstractShaftOrHousing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2179.AbstractShaftOrHousing.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractShaftOrHousing. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_abstract_shaft(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractShaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_fe_part(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2194.FEPart.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to FEPart. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Shaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CycloidalDisc. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
