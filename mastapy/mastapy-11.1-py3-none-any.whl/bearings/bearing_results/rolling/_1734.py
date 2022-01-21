'''_1734.py

LoadedAngularContactThrustBallBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1731
from mastapy._internal.python_net import python_net_import

_LOADED_ANGULAR_CONTACT_THRUST_BALL_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAngularContactThrustBallBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAngularContactThrustBallBearingElement',)


class LoadedAngularContactThrustBallBearingElement(_1731.LoadedAngularContactBallBearingElement):
    '''LoadedAngularContactThrustBallBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_ANGULAR_CONTACT_THRUST_BALL_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAngularContactThrustBallBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
