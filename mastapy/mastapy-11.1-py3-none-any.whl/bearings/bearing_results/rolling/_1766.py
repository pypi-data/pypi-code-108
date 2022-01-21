'''_1766.py

LoadedFourPointContactBallBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1751
from mastapy._internal.python_net import python_net_import

_LOADED_FOUR_POINT_CONTACT_BALL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedFourPointContactBallBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedFourPointContactBallBearingResults',)


class LoadedFourPointContactBallBearingResults(_1751.LoadedBallBearingResults):
    '''LoadedFourPointContactBallBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_FOUR_POINT_CONTACT_BALL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedFourPointContactBallBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
