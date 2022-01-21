'''_1732.py

LoadedAngularContactBallBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1751
from mastapy._internal.python_net import python_net_import

_LOADED_ANGULAR_CONTACT_BALL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAngularContactBallBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAngularContactBallBearingResults',)


class LoadedAngularContactBallBearingResults(_1751.LoadedBallBearingResults):
    '''LoadedAngularContactBallBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_ANGULAR_CONTACT_BALL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAngularContactBallBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
