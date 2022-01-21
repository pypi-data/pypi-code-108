'''_7259.py

ConnectionTimeSeriesLoadAnalysisCase
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7255
from mastapy._internal.python_net import python_net_import

_CONNECTION_TIME_SERIES_LOAD_ANALYSIS_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'ConnectionTimeSeriesLoadAnalysisCase')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionTimeSeriesLoadAnalysisCase',)


class ConnectionTimeSeriesLoadAnalysisCase(_7255.ConnectionAnalysisCase):
    '''ConnectionTimeSeriesLoadAnalysisCase

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_TIME_SERIES_LOAD_ANALYSIS_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionTimeSeriesLoadAnalysisCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
