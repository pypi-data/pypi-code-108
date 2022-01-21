'''_1864.py

ANSIABMA112014Results
'''


from mastapy.bearings.bearing_results.rolling.abma import _1866
from mastapy._internal.python_net import python_net_import

_ANSIABMA112014_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.ABMA', 'ANSIABMA112014Results')


__docformat__ = 'restructuredtext en'
__all__ = ('ANSIABMA112014Results',)


class ANSIABMA112014Results(_1866.ANSIABMAResults):
    '''ANSIABMA112014Results

    This is a mastapy class.
    '''

    TYPE = _ANSIABMA112014_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ANSIABMA112014Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
