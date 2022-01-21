'''_5040.py

KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4888
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5006
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis',)


class KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis(_5006.ConicalGearMeshCompoundModalAnalysis):
    '''KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4888.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4888.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4888.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4888.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis))
        return value
