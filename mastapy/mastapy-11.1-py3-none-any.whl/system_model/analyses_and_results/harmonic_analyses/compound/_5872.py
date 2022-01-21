'''_5872.py

BevelGearMeshCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5680
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5860
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'BevelGearMeshCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMeshCompoundHarmonicAnalysis',)


class BevelGearMeshCompoundHarmonicAnalysis(_5860.AGMAGleasonConicalGearMeshCompoundHarmonicAnalysis):
    '''BevelGearMeshCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMeshCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_5680.BevelGearMeshHarmonicAnalysis]':
        '''List[BevelGearMeshHarmonicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5680.BevelGearMeshHarmonicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5680.BevelGearMeshHarmonicAnalysis]':
        '''List[BevelGearMeshHarmonicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5680.BevelGearMeshHarmonicAnalysis))
        return value
