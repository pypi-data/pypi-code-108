'''_1785.py

LoadedSelfAligningBallBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1751
from mastapy._internal.python_net import python_net_import

_LOADED_SELF_ALIGNING_BALL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSelfAligningBallBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSelfAligningBallBearingResults',)


class LoadedSelfAligningBallBearingResults(_1751.LoadedBallBearingResults):
    '''LoadedSelfAligningBallBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_SELF_ALIGNING_BALL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSelfAligningBallBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
