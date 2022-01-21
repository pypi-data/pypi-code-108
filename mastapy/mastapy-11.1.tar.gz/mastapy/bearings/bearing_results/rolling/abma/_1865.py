'''_1865.py

ANSIABMA92015Results
'''


from mastapy.bearings.bearing_results.rolling.abma import _1866
from mastapy._internal.python_net import python_net_import

_ANSIABMA92015_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.ABMA', 'ANSIABMA92015Results')


__docformat__ = 'restructuredtext en'
__all__ = ('ANSIABMA92015Results',)


class ANSIABMA92015Results(_1866.ANSIABMAResults):
    '''ANSIABMA92015Results

    This is a mastapy class.
    '''

    TYPE = _ANSIABMA92015_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ANSIABMA92015Results.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
