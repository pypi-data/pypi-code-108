'''_1903.py

GeometricConstantsForRollingFrictionalMoments
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEOMETRIC_CONSTANTS_FOR_ROLLING_FRICTIONAL_MOMENTS = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'GeometricConstantsForRollingFrictionalMoments')


__docformat__ = 'restructuredtext en'
__all__ = ('GeometricConstantsForRollingFrictionalMoments',)


class GeometricConstantsForRollingFrictionalMoments(_0.APIBase):
    '''GeometricConstantsForRollingFrictionalMoments

    This is a mastapy class.
    '''

    TYPE = _GEOMETRIC_CONSTANTS_FOR_ROLLING_FRICTIONAL_MOMENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GeometricConstantsForRollingFrictionalMoments.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def r1(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'R1' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.R1) if self.wrapped.R1 is not None else None

    @r1.setter
    def r1(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.R1 = value

    @property
    def r2(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'R2' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.R2) if self.wrapped.R2 is not None else None

    @r2.setter
    def r2(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.R2 = value

    @property
    def r3(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'R3' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.R3) if self.wrapped.R3 is not None else None

    @r3.setter
    def r3(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.R3 = value

    @property
    def r4(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'R4' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.R4) if self.wrapped.R4 is not None else None

    @r4.setter
    def r4(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.R4 = value
