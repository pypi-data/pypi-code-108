'''_2365.py

CriticalSpeedAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CriticalSpeedAnalysis',)


class CriticalSpeedAnalysis(_2360.SingleAnalysis):
    '''CriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
