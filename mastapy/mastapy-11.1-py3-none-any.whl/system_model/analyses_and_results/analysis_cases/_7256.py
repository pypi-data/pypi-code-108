'''_7256.py

ConnectionCompoundAnalysis
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7260
from mastapy._internal.python_net import python_net_import

_CONNECTION_COMPOUND_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'ConnectionCompoundAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionCompoundAnalysis',)


class ConnectionCompoundAnalysis(_7260.DesignEntityCompoundAnalysis):
    '''ConnectionCompoundAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_COMPOUND_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionCompoundAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
