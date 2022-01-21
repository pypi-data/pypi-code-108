'''_1851.py

BallISO2812007Results
'''


from mastapy.bearings.bearing_results.rolling.iso_rating_results import _1853
from mastapy._internal.python_net import python_net_import

_BALL_ISO2812007_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.IsoRatingResults', 'BallISO2812007Results')


__docformat__ = 'restructuredtext en'
__all__ = ('BallISO2812007Results',)


class BallISO2812007Results(_1853.ISO2812007Results):
    '''BallISO2812007Results

    This is a mastapy class.
    '''

    TYPE = _BALL_ISO2812007_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BallISO2812007Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
