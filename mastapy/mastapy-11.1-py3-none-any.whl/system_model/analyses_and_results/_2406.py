'''_2406.py

CompoundDynamicModelForStabilityAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_DYNAMIC_MODEL_FOR_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundDynamicModelForStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundDynamicModelForStabilityAnalysis',)


class CompoundDynamicModelForStabilityAnalysis(_2359.CompoundAnalysis):
    '''CompoundDynamicModelForStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_DYNAMIC_MODEL_FOR_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundDynamicModelForStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
