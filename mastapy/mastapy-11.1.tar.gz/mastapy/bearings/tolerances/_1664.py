'''_1664.py

InterferenceDetail
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.bearings.tolerances import _1657
from mastapy._internal.python_net import python_net_import

_INTERFERENCE_DETAIL = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'InterferenceDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('InterferenceDetail',)


class InterferenceDetail(_1657.BearingConnectionComponent):
    '''InterferenceDetail

    This is a mastapy class.
    '''

    TYPE = _INTERFERENCE_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterferenceDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

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
    def diameter_tolerance_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterToleranceFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterToleranceFactor) if self.wrapped.DiameterToleranceFactor is not None else None

    @diameter_tolerance_factor.setter
    def diameter_tolerance_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DiameterToleranceFactor = value
