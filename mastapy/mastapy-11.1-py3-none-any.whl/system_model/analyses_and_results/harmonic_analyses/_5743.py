'''_5743.py

HarmonicAnalysisDrawStyle
'''


from mastapy.system_model.analyses_and_results.dynamic_analyses import _6045
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'HarmonicAnalysisDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisDrawStyle',)


class HarmonicAnalysisDrawStyle(_6045.DynamicAnalysisDrawStyle):
    '''HarmonicAnalysisDrawStyle

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
