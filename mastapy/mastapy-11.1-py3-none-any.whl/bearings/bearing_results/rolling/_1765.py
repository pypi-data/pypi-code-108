'''_1765.py

LoadedFourPointContactBallBearingRaceResults
'''


from mastapy.bearings.bearing_results.rolling import _1750
from mastapy._internal.python_net import python_net_import

_LOADED_FOUR_POINT_CONTACT_BALL_BEARING_RACE_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedFourPointContactBallBearingRaceResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedFourPointContactBallBearingRaceResults',)


class LoadedFourPointContactBallBearingRaceResults(_1750.LoadedBallBearingRaceResults):
    '''LoadedFourPointContactBallBearingRaceResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_FOUR_POINT_CONTACT_BALL_BEARING_RACE_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedFourPointContactBallBearingRaceResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
