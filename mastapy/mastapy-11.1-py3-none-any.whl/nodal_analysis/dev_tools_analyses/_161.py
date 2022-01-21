'''_161.py

FEModelHarmonicAnalysisDrawStyle
'''


from mastapy.nodal_analysis.dev_tools_analyses import _166
from mastapy._internal.python_net import python_net_import

_FE_MODEL_HARMONIC_ANALYSIS_DRAW_STYLE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FEModelHarmonicAnalysisDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('FEModelHarmonicAnalysisDrawStyle',)


class FEModelHarmonicAnalysisDrawStyle(_166.FEModelTabDrawStyle):
    '''FEModelHarmonicAnalysisDrawStyle

    This is a mastapy class.
    '''

    TYPE = _FE_MODEL_HARMONIC_ANALYSIS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEModelHarmonicAnalysisDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
