'''_2377.py

ModalAnalysisAtAStiffness
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'ModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('ModalAnalysisAtAStiffness',)


class ModalAnalysisAtAStiffness(_2360.SingleAnalysis):
    '''ModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
