'''_6298.py

CriticalSpeedAnalysisDrawStyle
'''


from mastapy.system_model.analyses_and_results.rotor_dynamics import _3759
from mastapy._internal.python_net import python_net_import

_CRITICAL_SPEED_ANALYSIS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'CriticalSpeedAnalysisDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('CriticalSpeedAnalysisDrawStyle',)


class CriticalSpeedAnalysisDrawStyle(_3759.RotorDynamicsDrawStyle):
    '''CriticalSpeedAnalysisDrawStyle

    This is a mastapy class.
    '''

    TYPE = _CRITICAL_SPEED_ANALYSIS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CriticalSpeedAnalysisDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
