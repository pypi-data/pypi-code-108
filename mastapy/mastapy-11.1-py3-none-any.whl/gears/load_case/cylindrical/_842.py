'''_842.py

CylindricalGearLoadCase
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.gears.load_case import _833
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Cylindrical', 'CylindricalGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearLoadCase',)


class CylindricalGearLoadCase(_833.GearLoadCaseBase):
    '''CylindricalGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def reversed_bending_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReversedBendingFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReversedBendingFactor) if self.wrapped.ReversedBendingFactor is not None else None

    @reversed_bending_factor.setter
    def reversed_bending_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ReversedBendingFactor = value
