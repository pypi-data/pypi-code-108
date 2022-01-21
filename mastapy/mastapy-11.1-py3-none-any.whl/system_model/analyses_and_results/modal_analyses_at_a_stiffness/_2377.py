'''_2377.py

ModalAnalysisAtAStiffness
'''


from mastapy.system_model.analyses_and_results.analysis_cases import _7267
from mastapy._internal.python_net import python_net_import

_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness', 'ModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('ModalAnalysisAtAStiffness',)


class ModalAnalysisAtAStiffness(_7267.StaticLoadAnalysisCase):
    '''ModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
