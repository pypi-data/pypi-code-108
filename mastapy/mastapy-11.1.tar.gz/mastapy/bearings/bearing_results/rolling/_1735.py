'''_1735.py

LoadedAngularContactThrustBallBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1732
from mastapy._internal.python_net import python_net_import

_LOADED_ANGULAR_CONTACT_THRUST_BALL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAngularContactThrustBallBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAngularContactThrustBallBearingResults',)


class LoadedAngularContactThrustBallBearingResults(_1732.LoadedAngularContactBallBearingResults):
    '''LoadedAngularContactThrustBallBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_ANGULAR_CONTACT_THRUST_BALL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAngularContactThrustBallBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
