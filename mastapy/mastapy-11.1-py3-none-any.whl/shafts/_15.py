'''_15.py

ProfilePointFilletStressConcentrationFactors
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PROFILE_POINT_FILLET_STRESS_CONCENTRATION_FACTORS = python_net_import('SMT.MastaAPI.Shafts', 'ProfilePointFilletStressConcentrationFactors')


__docformat__ = 'restructuredtext en'
__all__ = ('ProfilePointFilletStressConcentrationFactors',)


class ProfilePointFilletStressConcentrationFactors(_0.APIBase):
    '''ProfilePointFilletStressConcentrationFactors

    This is a mastapy class.
    '''

    TYPE = _PROFILE_POINT_FILLET_STRESS_CONCENTRATION_FACTORS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ProfilePointFilletStressConcentrationFactors.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Bending' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Bending) if self.wrapped.Bending is not None else None

    @bending.setter
    def bending(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Bending = value

    @property
    def tension(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Tension' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Tension) if self.wrapped.Tension is not None else None

    @tension.setter
    def tension(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Tension = value

    @property
    def torsion(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Torsion' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Torsion) if self.wrapped.Torsion is not None else None

    @torsion.setter
    def torsion(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Torsion = value
