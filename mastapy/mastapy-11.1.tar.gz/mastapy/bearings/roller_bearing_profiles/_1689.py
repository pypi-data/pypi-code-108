'''_1689.py

RollerBearingJohnsGoharProfile
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.bearings.roller_bearing_profiles import _1691
from mastapy._internal.python_net import python_net_import

_ROLLER_BEARING_JOHNS_GOHAR_PROFILE = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'RollerBearingJohnsGoharProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerBearingJohnsGoharProfile',)


class RollerBearingJohnsGoharProfile(_1691.RollerBearingProfile):
    '''RollerBearingJohnsGoharProfile

    This is a mastapy class.
    '''

    TYPE = _ROLLER_BEARING_JOHNS_GOHAR_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerBearingJohnsGoharProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length_factor(self) -> 'float':
        '''float: 'LengthFactor' is the original name of this property.'''

        return self.wrapped.LengthFactor

    @length_factor.setter
    def length_factor(self, value: 'float'):
        self.wrapped.LengthFactor = float(value) if value else 0.0

    @property
    def end_drop(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'EndDrop' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.EndDrop) if self.wrapped.EndDrop is not None else None

    @end_drop.setter
    def end_drop(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.EndDrop = value

    @property
    def design_load(self) -> 'float':
        '''float: 'DesignLoad' is the original name of this property.'''

        return self.wrapped.DesignLoad

    @design_load.setter
    def design_load(self, value: 'float'):
        self.wrapped.DesignLoad = float(value) if value else 0.0
