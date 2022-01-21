'''_1891.py

BarrelRollerBearing
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.bearings.bearing_designs.rolling import _1909
from mastapy._internal.python_net import python_net_import

_BARREL_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'BarrelRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('BarrelRollerBearing',)


class BarrelRollerBearing(_1909.RollerBearing):
    '''BarrelRollerBearing

    This is a mastapy class.
    '''

    TYPE = _BARREL_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BarrelRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def groove_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'GrooveRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.GrooveRadius) if self.wrapped.GrooveRadius is not None else None

    @groove_radius.setter
    def groove_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.GrooveRadius = value

    @property
    def element_profile_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementProfileRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementProfileRadius) if self.wrapped.ElementProfileRadius is not None else None

    @element_profile_radius.setter
    def element_profile_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementProfileRadius = value

    @property
    def roller_race_radius_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RollerRaceRadiusRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RollerRaceRadiusRatio) if self.wrapped.RollerRaceRadiusRatio is not None else None

    @roller_race_radius_ratio.setter
    def roller_race_radius_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RollerRaceRadiusRatio = value
