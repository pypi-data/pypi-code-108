'''_1044.py

NominalValueSpecification
'''


from typing import Generic, TypeVar

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _1037
from mastapy._internal.python_net import python_net_import

_NOMINAL_VALUE_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.ThicknessStockAndBacklash', 'NominalValueSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('NominalValueSpecification',)


T = TypeVar('T')


class NominalValueSpecification(_1037.TolerancedValueSpecification['T'], Generic[T]):
    '''NominalValueSpecification

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _NOMINAL_VALUE_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NominalValueSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def design(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Design' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Design) if self.wrapped.Design is not None else None

    @design.setter
    def design(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Design = value
