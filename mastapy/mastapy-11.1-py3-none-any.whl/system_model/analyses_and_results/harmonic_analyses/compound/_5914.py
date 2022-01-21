'''_5914.py

GearMeshCompoundHarmonicAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses import _5737
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.harmonic_analyses.compound import _5920
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound', 'GearMeshCompoundHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundHarmonicAnalysis',)


class GearMeshCompoundHarmonicAnalysis(_5920.InterMountableComponentConnectionCompoundHarmonicAnalysis):
    '''GearMeshCompoundHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_5737.GearMeshHarmonicAnalysis]':
        '''List[GearMeshHarmonicAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_5737.GearMeshHarmonicAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_5737.GearMeshHarmonicAnalysis]':
        '''List[GearMeshHarmonicAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_5737.GearMeshHarmonicAnalysis))
        return value
