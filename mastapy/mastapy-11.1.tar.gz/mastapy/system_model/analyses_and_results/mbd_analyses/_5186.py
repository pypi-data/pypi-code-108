'''_5186.py

MBDAnalysisDrawStyle
'''


from mastapy.system_model.drawing import _1987
from mastapy._internal.python_net import python_net_import

_MBD_ANALYSIS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'MBDAnalysisDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('MBDAnalysisDrawStyle',)


class MBDAnalysisDrawStyle(_1987.ContourDrawStyle):
    '''MBDAnalysisDrawStyle

    This is a mastapy class.
    '''

    TYPE = _MBD_ANALYSIS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MBDAnalysisDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
