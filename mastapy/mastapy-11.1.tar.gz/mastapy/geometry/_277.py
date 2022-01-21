'''_277.py

PackagingLimits
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_PACKAGING_LIMITS = python_net_import('SMT.MastaAPI.Geometry', 'PackagingLimits')


__docformat__ = 'restructuredtext en'
__all__ = ('PackagingLimits',)


class PackagingLimits(_1382.IndependentReportablePropertiesBase['PackagingLimits']):
    '''PackagingLimits

    This is a mastapy class.
    '''

    TYPE = _PACKAGING_LIMITS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PackagingLimits.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_x(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumX' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumX) if self.wrapped.MaximumX is not None else None

    @maximum_x.setter
    def maximum_x(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumX = value

    @property
    def minimum_x(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumX' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumX) if self.wrapped.MinimumX is not None else None

    @minimum_x.setter
    def minimum_x(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumX = value

    @property
    def maximum_y(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumY' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumY) if self.wrapped.MaximumY is not None else None

    @maximum_y.setter
    def maximum_y(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumY = value

    @property
    def minimum_y(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumY' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumY) if self.wrapped.MinimumY is not None else None

    @minimum_y.setter
    def minimum_y(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumY = value

    @property
    def maximum_z(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumZ) if self.wrapped.MaximumZ is not None else None

    @maximum_z.setter
    def maximum_z(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumZ = value

    @property
    def minimum_z(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumZ) if self.wrapped.MinimumZ is not None else None

    @minimum_z.setter
    def minimum_z(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumZ = value
