'''_2370.py

DynamicModelForStabilityAnalysis
'''


from mastapy.system_model.analyses_and_results.dynamic_analyses import _2366
from mastapy._internal.python_net import python_net_import

_DYNAMIC_MODEL_FOR_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'DynamicModelForStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicModelForStabilityAnalysis',)


class DynamicModelForStabilityAnalysis(_2366.DynamicAnalysis):
    '''DynamicModelForStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_MODEL_FOR_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicModelForStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
