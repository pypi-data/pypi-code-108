'''_7257.py

ConnectionFEAnalysis
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7258
from mastapy._internal.python_net import python_net_import

_CONNECTION_FE_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'ConnectionFEAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionFEAnalysis',)


class ConnectionFEAnalysis(_7258.ConnectionStaticLoadAnalysisCase):
    '''ConnectionFEAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_FE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionFEAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
