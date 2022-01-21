'''_2412.py

CompoundModalAnalysisAtASpeed
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundModalAnalysisAtASpeed',)


class CompoundModalAnalysisAtASpeed(_2359.CompoundAnalysis):
    '''CompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
