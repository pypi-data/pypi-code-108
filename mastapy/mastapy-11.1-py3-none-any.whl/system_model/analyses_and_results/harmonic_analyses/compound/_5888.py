'''_5888.py

ConicalGearMeshCompoundHarmonicAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5697
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5914
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'ConicalGearMeshCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundHarmonicAnalysis',)


class ConicalGearMeshCompoundHarmonicAnalysis(_5914.GearMeshCompoundHarmonicAnalysis):
    '''ConicalGearMeshCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundHarmonicAnalysis]':
        '''List[ConicalGearMeshCompoundHarmonicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundHarmonicAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_5697.ConicalGearMeshHarmonicAnalysis]':
        '''List[ConicalGearMeshHarmonicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5697.ConicalGearMeshHarmonicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5697.ConicalGearMeshHarmonicAnalysis]':
        '''List[ConicalGearMeshHarmonicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5697.ConicalGearMeshHarmonicAnalysis))
        return value
