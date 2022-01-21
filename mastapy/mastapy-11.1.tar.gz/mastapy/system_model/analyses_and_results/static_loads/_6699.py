'''_6699.py

UnbalancedMassLoadCase
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.part_model import _2218
from mastapy.system_model.analyses_and_results.static_loads import _6700
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'UnbalancedMassLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassLoadCase',)


class UnbalancedMassLoadCase(_6700.VirtualComponentLoadCase):
    '''UnbalancedMassLoadCase

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Radius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Radius) if self.wrapped.Radius is not None else None

    @radius.setter
    def radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Radius = value

    @property
    def angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Angle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Angle) if self.wrapped.Angle is not None else None

    @angle.setter
    def angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Angle = value

    @property
    def mass(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Mass' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Mass) if self.wrapped.Mass is not None else None

    @mass.setter
    def mass(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Mass = value

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
