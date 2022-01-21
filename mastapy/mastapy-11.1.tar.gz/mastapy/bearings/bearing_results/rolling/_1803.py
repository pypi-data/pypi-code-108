'''_1803.py

LoadedThrustBallBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1749
from mastapy._internal.python_net import python_net_import

_LOADED_THRUST_BALL_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedThrustBallBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedThrustBallBearingElement',)


class LoadedThrustBallBearingElement(_1749.LoadedBallBearingElement):
    '''LoadedThrustBallBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_THRUST_BALL_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedThrustBallBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
