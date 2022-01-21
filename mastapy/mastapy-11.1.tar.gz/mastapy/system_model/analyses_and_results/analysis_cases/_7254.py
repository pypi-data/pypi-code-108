'''_7254.py

CompoundAnalysisCase
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7267
from mastapy._internal.python_net import python_net_import

_COMPOUND_ANALYSIS_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'CompoundAnalysisCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundAnalysisCase',)


class CompoundAnalysisCase(_7267.StaticLoadAnalysisCase):
    '''CompoundAnalysisCase

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_ANALYSIS_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundAnalysisCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
