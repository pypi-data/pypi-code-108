'''_1699.py

EquivalentLoadFactors
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_EQUIVALENT_LOAD_FACTORS = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'EquivalentLoadFactors')


__docformat__ = 'restructuredtext en'
__all__ = ('EquivalentLoadFactors',)


class EquivalentLoadFactors(_1382.IndependentReportablePropertiesBase['EquivalentLoadFactors']):
    '''EquivalentLoadFactors

    This is a mastapy class.
    '''

    TYPE = _EQUIVALENT_LOAD_FACTORS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EquivalentLoadFactors.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial_load_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AxialLoadFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AxialLoadFactor) if self.wrapped.AxialLoadFactor is not None else None

    @axial_load_factor.setter
    def axial_load_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AxialLoadFactor = value

    @property
    def radial_load_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadialLoadFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadialLoadFactor) if self.wrapped.RadialLoadFactor is not None else None

    @radial_load_factor.setter
    def radial_load_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RadialLoadFactor = value
