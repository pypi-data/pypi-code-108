'''_1988.py

CriticalSpeedAnalysisViewable
'''


from mastapy.system_model.drawing import _1996
from mastapy._internal.python_net import python_net_import

_CRITICAL_SPEED_ANALYSIS_VIEWABLE = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'CriticalSpeedAnalysisViewable')


__docformat__ = 'restructuredtext en'
__all__ = ('CriticalSpeedAnalysisViewable',)


class CriticalSpeedAnalysisViewable(_1996.RotorDynamicsViewable):
    '''CriticalSpeedAnalysisViewable

    This is a mastapy class.
    '''

    TYPE = _CRITICAL_SPEED_ANALYSIS_VIEWABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CriticalSpeedAnalysisViewable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
