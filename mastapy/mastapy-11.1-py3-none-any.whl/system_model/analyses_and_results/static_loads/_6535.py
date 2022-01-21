'''_6535.py

BeltConnectionLoadCase
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.connections_and_sockets import _2010, _2015
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6628
from mastapy._internal.python_net import python_net_import

_BELT_CONNECTION_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'BeltConnectionLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('BeltConnectionLoadCase',)


class BeltConnectionLoadCase(_6628.InterMountableComponentConnectionLoadCase):
    '''BeltConnectionLoadCase

    This is a mastapy class.
    '''

    TYPE = _BELT_CONNECTION_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BeltConnectionLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pre_extension(self) -> 'float':
        '''float: 'PreExtension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PreExtension

    @property
    def rayleigh_damping_beta(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RayleighDampingBeta' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RayleighDampingBeta) if self.wrapped.RayleighDampingBeta is not None else None

    @rayleigh_damping_beta.setter
    def rayleigh_damping_beta(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RayleighDampingBeta = value

    @property
    def connection_design(self) -> '_2010.BeltConnection':
        '''BeltConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2010.BeltConnection.TYPE not in self.wrapped.ConnectionDesign.__class__.__mro__:
            raise CastException('Failed to cast connection_design to BeltConnection. Expected: {}.'.format(self.wrapped.ConnectionDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConnectionDesign.__class__)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
