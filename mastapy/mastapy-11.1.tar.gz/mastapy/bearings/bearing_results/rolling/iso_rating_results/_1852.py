'''_1852.py

BallISOTS162812008Results
'''


from mastapy.bearings.bearing_results.rolling.iso_rating_results import _1856
from mastapy._internal.python_net import python_net_import

_BALL_ISOTS162812008_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.IsoRatingResults', 'BallISOTS162812008Results')


__docformat__ = 'restructuredtext en'
__all__ = ('BallISOTS162812008Results',)


class BallISOTS162812008Results(_1856.ISOTS162812008Results):
    '''BallISOTS162812008Results

    This is a mastapy class.
    '''

    TYPE = _BALL_ISOTS162812008_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BallISOTS162812008Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
