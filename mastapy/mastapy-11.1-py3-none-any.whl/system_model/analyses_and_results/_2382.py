'''_2382.py

StabilityAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'StabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StabilityAnalysis',)


class StabilityAnalysis(_2360.SingleAnalysis):
    '''StabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
