'''_1750.py

LoadedBallBearingRaceResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1781
from mastapy._internal.python_net import python_net_import

_LOADED_BALL_BEARING_RACE_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedBallBearingRaceResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBallBearingRaceResults',)


class LoadedBallBearingRaceResults(_1781.LoadedRollingBearingRaceResults):
    '''LoadedBallBearingRaceResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_BALL_BEARING_RACE_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedBallBearingRaceResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_radius_at_right_angles_to_rolling_direction(self) -> 'float':
        '''float: 'ContactRadiusAtRightAnglesToRollingDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRadiusAtRightAnglesToRollingDirection

    @property
    def hertzian_semi_minor_dimension_highest_load(self) -> 'float':
        '''float: 'HertzianSemiMinorDimensionHighestLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMinorDimensionHighestLoad

    @property
    def hertzian_semi_major_dimension_highest_load(self) -> 'float':
        '''float: 'HertzianSemiMajorDimensionHighestLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMajorDimensionHighestLoad
