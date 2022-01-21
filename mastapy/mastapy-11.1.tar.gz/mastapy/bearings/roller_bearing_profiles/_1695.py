'''_1695.py

UserSpecifiedRollerRaceProfilePoint
'''


from mastapy._internal import constructor
from mastapy.bearings.roller_bearing_profiles import _1693
from mastapy._internal.python_net import python_net_import

_USER_SPECIFIED_ROLLER_RACE_PROFILE_POINT = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'UserSpecifiedRollerRaceProfilePoint')


__docformat__ = 'restructuredtext en'
__all__ = ('UserSpecifiedRollerRaceProfilePoint',)


class UserSpecifiedRollerRaceProfilePoint(_1693.RollerRaceProfilePoint):
    '''UserSpecifiedRollerRaceProfilePoint

    This is a mastapy class.
    '''

    TYPE = _USER_SPECIFIED_ROLLER_RACE_PROFILE_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UserSpecifiedRollerRaceProfilePoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def roller_analysis_deviation(self) -> 'float':
        '''float: 'RollerAnalysisDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollerAnalysisDeviation

    @property
    def race_analysis_deviation(self) -> 'float':
        '''float: 'RaceAnalysisDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RaceAnalysisDeviation
