'''_4990.py

BevelGearMeshCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4836
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4978
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'BevelGearMeshCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMeshCompoundModalAnalysis',)


class BevelGearMeshCompoundModalAnalysis(_4978.AGMAGleasonConicalGearMeshCompoundModalAnalysis):
    '''BevelGearMeshCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMeshCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4836.BevelGearMeshModalAnalysis]':
        '''List[BevelGearMeshModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4836.BevelGearMeshModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4836.BevelGearMeshModalAnalysis]':
        '''List[BevelGearMeshModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4836.BevelGearMeshModalAnalysis))
        return value
