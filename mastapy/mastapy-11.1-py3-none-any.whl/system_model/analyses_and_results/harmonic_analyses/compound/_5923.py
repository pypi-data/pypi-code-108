'''_5923.py

KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5755
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5889
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysis',)


class KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysis(_5889.ConicalGearSetCompoundHarmonicAnalysis):
    '''KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_5755.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_5755.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_5755.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_5755.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis))
        return value
