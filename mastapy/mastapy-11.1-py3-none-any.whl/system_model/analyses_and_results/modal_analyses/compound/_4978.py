'''_4978.py

AGMAGleasonConicalGearMeshCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4824
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5006
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'AGMAGleasonConicalGearMeshCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundModalAnalysis',)


class AGMAGleasonConicalGearMeshCompoundModalAnalysis(_5006.ConicalGearMeshCompoundModalAnalysis):
    '''AGMAGleasonConicalGearMeshCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4824.AGMAGleasonConicalGearMeshModalAnalysis]':
        '''List[AGMAGleasonConicalGearMeshModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4824.AGMAGleasonConicalGearMeshModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4824.AGMAGleasonConicalGearMeshModalAnalysis]':
        '''List[AGMAGleasonConicalGearMeshModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4824.AGMAGleasonConicalGearMeshModalAnalysis))
        return value
