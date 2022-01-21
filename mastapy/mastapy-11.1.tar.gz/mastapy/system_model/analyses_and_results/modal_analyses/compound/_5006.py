'''_5006.py

ConicalGearMeshCompoundModalAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4852
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5032
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'ConicalGearMeshCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundModalAnalysis',)


class ConicalGearMeshCompoundModalAnalysis(_5032.GearMeshCompoundModalAnalysis):
    '''ConicalGearMeshCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundModalAnalysis]':
        '''List[ConicalGearMeshCompoundModalAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundModalAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_4852.ConicalGearMeshModalAnalysis]':
        '''List[ConicalGearMeshModalAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4852.ConicalGearMeshModalAnalysis))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4852.ConicalGearMeshModalAnalysis]':
        '''List[ConicalGearMeshModalAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4852.ConicalGearMeshModalAnalysis))
        return value
