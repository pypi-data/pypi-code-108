'''_1693.py

RollerRaceProfilePoint
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ROLLER_RACE_PROFILE_POINT = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'RollerRaceProfilePoint')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerRaceProfilePoint',)


class RollerRaceProfilePoint(_0.APIBase):
    '''RollerRaceProfilePoint

    This is a mastapy class.
    '''

    TYPE = _ROLLER_RACE_PROFILE_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerRaceProfilePoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def offset_from_roller_centre(self) -> 'float':
        '''float: 'OffsetFromRollerCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OffsetFromRollerCentre

    @property
    def roller_deviation(self) -> 'float':
        '''float: 'RollerDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollerDeviation

    @property
    def race_deviation(self) -> 'float':
        '''float: 'RaceDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RaceDeviation

    @property
    def total_deviation(self) -> 'float':
        '''float: 'TotalDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalDeviation
