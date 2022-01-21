'''_2417.py

CompoundStabilityAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundStabilityAnalysis',)


class CompoundStabilityAnalysis(_2359.CompoundAnalysis):
    '''CompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
