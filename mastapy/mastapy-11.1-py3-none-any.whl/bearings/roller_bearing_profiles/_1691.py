'''_1691.py

RollerBearingProfile
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ROLLER_BEARING_PROFILE = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'RollerBearingProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerBearingProfile',)


class RollerBearingProfile(_0.APIBase):
    '''RollerBearingProfile

    This is a mastapy class.
    '''

    TYPE = _ROLLER_BEARING_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerBearingProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def covers_two_rows_of_elements(self) -> 'bool':
        '''bool: 'CoversTwoRowsOfElements' is the original name of this property.'''

        return self.wrapped.CoversTwoRowsOfElements

    @covers_two_rows_of_elements.setter
    def covers_two_rows_of_elements(self, value: 'bool'):
        self.wrapped.CoversTwoRowsOfElements = bool(value) if value else False
