'''_7265.py

PartStaticLoadAnalysisCase
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7262
from mastapy._internal.python_net import python_net_import

_PART_STATIC_LOAD_ANALYSIS_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'PartStaticLoadAnalysisCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PartStaticLoadAnalysisCase',)


class PartStaticLoadAnalysisCase(_7262.PartAnalysisCase):
    '''PartStaticLoadAnalysisCase

    This is a mastapy class.
    '''

    TYPE = _PART_STATIC_LOAD_ANALYSIS_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartStaticLoadAnalysisCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
