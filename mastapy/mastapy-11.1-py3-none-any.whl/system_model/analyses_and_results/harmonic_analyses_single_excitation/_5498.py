'''_5498.py

RootAssemblyHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model import _2215
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5465, _5410
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'RootAssemblyHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyHarmonicAnalysisOfSingleExcitation',)


class RootAssemblyHarmonicAnalysisOfSingleExcitation(_5410.AssemblyHarmonicAnalysisOfSingleExcitation):
    '''RootAssemblyHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2215.RootAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def harmonic_analysis_of_single_excitation_inputs(self) -> '_5465.HarmonicAnalysisOfSingleExcitation':
        '''HarmonicAnalysisOfSingleExcitation: 'HarmonicAnalysisOfSingleExcitationInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5465.HarmonicAnalysisOfSingleExcitation)(self.wrapped.HarmonicAnalysisOfSingleExcitationInputs) if self.wrapped.HarmonicAnalysisOfSingleExcitationInputs is not None else None
