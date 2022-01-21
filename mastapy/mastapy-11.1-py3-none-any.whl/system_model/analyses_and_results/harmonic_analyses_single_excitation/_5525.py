'''_5525.py

UnbalancedMassHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6699
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5526
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'UnbalancedMassHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassHarmonicAnalysisOfSingleExcitation',)


class UnbalancedMassHarmonicAnalysisOfSingleExcitation(_5526.VirtualComponentHarmonicAnalysisOfSingleExcitation):
    '''UnbalancedMassHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6699.UnbalancedMassLoadCase':
        '''UnbalancedMassLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6699.UnbalancedMassLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
