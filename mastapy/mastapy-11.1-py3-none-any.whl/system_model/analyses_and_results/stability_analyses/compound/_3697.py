'''_3697.py

KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3565
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3663
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis',)


class KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis(_3663.ConicalGearMeshCompoundStabilityAnalysis):
    '''KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_3565.KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3565.KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3565.KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3565.KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis))
        return value
