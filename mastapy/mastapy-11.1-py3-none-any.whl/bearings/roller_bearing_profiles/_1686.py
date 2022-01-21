'''_1686.py

RollerBearingCrownedProfile
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.bearings.roller_bearing_profiles import _1691
from mastapy._internal.python_net import python_net_import

_ROLLER_BEARING_CROWNED_PROFILE = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'RollerBearingCrownedProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerBearingCrownedProfile',)


class RollerBearingCrownedProfile(_1691.RollerBearingProfile):
    '''RollerBearingCrownedProfile

    This is a mastapy class.
    '''

    TYPE = _ROLLER_BEARING_CROWNED_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerBearingCrownedProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def crown_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CrownRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CrownRadius) if self.wrapped.CrownRadius is not None else None

    @crown_radius.setter
    def crown_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CrownRadius = value

    @property
    def crown_end_drop(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CrownEndDrop' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CrownEndDrop) if self.wrapped.CrownEndDrop is not None else None

    @crown_end_drop.setter
    def crown_end_drop(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CrownEndDrop = value

    @property
    def parallel_length(self) -> 'float':
        '''float: 'ParallelLength' is the original name of this property.'''

        return self.wrapped.ParallelLength

    @parallel_length.setter
    def parallel_length(self, value: 'float'):
        self.wrapped.ParallelLength = float(value) if value else 0.0

    @property
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.'''

        return self.wrapped.Offset

    @offset.setter
    def offset(self, value: 'float'):
        self.wrapped.Offset = float(value) if value else 0.0
