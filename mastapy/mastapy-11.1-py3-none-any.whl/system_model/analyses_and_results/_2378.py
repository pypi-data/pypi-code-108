'''_2378.py

ModalAnalysisForHarmonicAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_MODAL_ANALYSIS_FOR_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'ModalAnalysisForHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ModalAnalysisForHarmonicAnalysis',)


class ModalAnalysisForHarmonicAnalysis(_2360.SingleAnalysis):
    '''ModalAnalysisForHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MODAL_ANALYSIS_FOR_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModalAnalysisForHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
