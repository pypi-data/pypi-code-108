'''_2378.py

ModalAnalysisForHarmonicAnalysis
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import _5746
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6790
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.modal_analyses import _2375
from mastapy._internal.python_net import python_net_import

_MODAL_ANALYSIS_FOR_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'ModalAnalysisForHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ModalAnalysisForHarmonicAnalysis',)


class ModalAnalysisForHarmonicAnalysis(_2375.ModalAnalysis):
    '''ModalAnalysisForHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MODAL_ANALYSIS_FOR_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModalAnalysisForHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def harmonic_analysis_settings(self) -> '_5746.HarmonicAnalysisOptions':
        '''HarmonicAnalysisOptions: 'HarmonicAnalysisSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5746.HarmonicAnalysisOptions.TYPE not in self.wrapped.HarmonicAnalysisSettings.__class__.__mro__:
            raise CastException('Failed to cast harmonic_analysis_settings to HarmonicAnalysisOptions. Expected: {}.'.format(self.wrapped.HarmonicAnalysisSettings.__class__.__qualname__))

        return constructor.new_override(self.wrapped.HarmonicAnalysisSettings.__class__)(self.wrapped.HarmonicAnalysisSettings) if self.wrapped.HarmonicAnalysisSettings is not None else None
