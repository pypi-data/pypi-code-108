'''_3604.py

StabilityAnalysisDrawStyle
'''


from mastapy.system_model.analyses_and_results.rotor_dynamics import _3759
from mastapy._internal.python_net import python_net_import

_STABILITY_ANALYSIS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'StabilityAnalysisDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('StabilityAnalysisDrawStyle',)


class StabilityAnalysisDrawStyle(_3759.RotorDynamicsDrawStyle):
    '''StabilityAnalysisDrawStyle

    This is a mastapy class.
    '''

    TYPE = _STABILITY_ANALYSIS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StabilityAnalysisDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
