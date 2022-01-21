'''_2366.py

DynamicAnalysis
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7261
from mastapy._internal.python_net import python_net_import

_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'DynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicAnalysis',)


class DynamicAnalysis(_7261.FEAnalysis):
    '''DynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
