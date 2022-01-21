'''_1784.py

LoadedSelfAligningBallBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1749
from mastapy._internal.python_net import python_net_import

_LOADED_SELF_ALIGNING_BALL_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSelfAligningBallBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSelfAligningBallBearingElement',)


class LoadedSelfAligningBallBearingElement(_1749.LoadedBallBearingElement):
    '''LoadedSelfAligningBallBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_SELF_ALIGNING_BALL_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSelfAligningBallBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
