'''_5032.py

GearMeshCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4880
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5038
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'GearMeshCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundModalAnalysis',)


class GearMeshCompoundModalAnalysis(_5038.InterMountableComponentConnectionCompoundModalAnalysis):
    '''GearMeshCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4880.GearMeshModalAnalysis]':
        '''List[GearMeshModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4880.GearMeshModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4880.GearMeshModalAnalysis]':
        '''List[GearMeshModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4880.GearMeshModalAnalysis))
        return value
