'''_1690.py

RollerBearingLundbergProfile
'''


from mastapy._internal import constructor
from mastapy.bearings.roller_bearing_profiles import _1691
from mastapy._internal.python_net import python_net_import

_ROLLER_BEARING_LUNDBERG_PROFILE = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'RollerBearingLundbergProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerBearingLundbergProfile',)


class RollerBearingLundbergProfile(_1691.RollerBearingProfile):
    '''RollerBearingLundbergProfile

    This is a mastapy class.
    '''

    TYPE = _ROLLER_BEARING_LUNDBERG_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerBearingLundbergProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_bearing_dynamic_capacity(self) -> 'bool':
        '''bool: 'UseBearingDynamicCapacity' is the original name of this property.'''

        return self.wrapped.UseBearingDynamicCapacity

    @use_bearing_dynamic_capacity.setter
    def use_bearing_dynamic_capacity(self, value: 'bool'):
        self.wrapped.UseBearingDynamicCapacity = bool(value) if value else False

    @property
    def load(self) -> 'float':
        '''float: 'Load' is the original name of this property.'''

        return self.wrapped.Load

    @load.setter
    def load(self, value: 'float'):
        self.wrapped.Load = float(value) if value else 0.0
