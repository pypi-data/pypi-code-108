'''_6522.py

AbstractShaftLoadCase
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.part_model import _2178
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.cycloidal import _2309
from mastapy.system_model.analyses_and_results.static_loads import _6523
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'AbstractShaftLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftLoadCase',)


class AbstractShaftLoadCase(_6523.AbstractShaftOrHousingLoadCase):
    '''AbstractShaftLoadCase

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaft_temperature(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ShaftTemperature' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ShaftTemperature) if self.wrapped.ShaftTemperature is not None else None

    @shaft_temperature.setter
    def shaft_temperature(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ShaftTemperature = value

    @property
    def component_design(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractShaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

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
