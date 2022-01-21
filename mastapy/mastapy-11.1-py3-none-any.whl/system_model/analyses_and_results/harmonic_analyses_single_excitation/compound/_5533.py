'''_5533.py

AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5403
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import _5612
from mastapy._internal.python_net import python_net_import

_ABSTRACT_ASSEMBLY_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound', 'AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation',)


class AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation(_5612.PartCompoundHarmonicAnalysisOfSingleExcitation):
    '''AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_ASSEMBLY_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_5403.AbstractAssemblyHarmonicAnalysisOfSingleExcitation]':
        '''List[AbstractAssemblyHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5403.AbstractAssemblyHarmonicAnalysisOfSingleExcitation))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5403.AbstractAssemblyHarmonicAnalysisOfSingleExcitation]':
        '''List[AbstractAssemblyHarmonicAnalysisOfSingleExcitation]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5403.AbstractAssemblyHarmonicAnalysisOfSingleExcitation))
        return value
