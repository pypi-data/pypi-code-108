'''_7264.py

PartFEAnalysis
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7265
from mastapy._internal.python_net import python_net_import

_PART_FE_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'PartFEAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartFEAnalysis',)


class PartFEAnalysis(_7265.PartStaticLoadAnalysisCase):
    '''PartFEAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_FE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartFEAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
