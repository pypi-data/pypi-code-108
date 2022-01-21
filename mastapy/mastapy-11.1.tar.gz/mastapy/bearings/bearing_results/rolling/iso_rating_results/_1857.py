'''_1857.py

RollerISO2812007Results
'''


from mastapy.bearings.bearing_results.rolling.iso_rating_results import _1853
from mastapy._internal.python_net import python_net_import

_ROLLER_ISO2812007_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.IsoRatingResults', 'RollerISO2812007Results')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerISO2812007Results',)


class RollerISO2812007Results(_1853.ISO2812007Results):
    '''RollerISO2812007Results

    This is a mastapy class.
    '''

    TYPE = _ROLLER_ISO2812007_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollerISO2812007Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
