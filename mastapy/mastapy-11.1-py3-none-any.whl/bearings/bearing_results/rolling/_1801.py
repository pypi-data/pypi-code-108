'''_1801.py

LoadedThreePointContactBallBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1751
from mastapy._internal.python_net import python_net_import

_LOADED_THREE_POINT_CONTACT_BALL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedThreePointContactBallBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedThreePointContactBallBearingResults',)


class LoadedThreePointContactBallBearingResults(_1751.LoadedBallBearingResults):
    '''LoadedThreePointContactBallBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_THREE_POINT_CONTACT_BALL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedThreePointContactBallBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
