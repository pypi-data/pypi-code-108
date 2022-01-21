'''_4237.py

HypoidGearMeshCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.connections_and_sockets.gears import _2057
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4096
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4179
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'HypoidGearMeshCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearMeshCompoundParametricStudyTool',)


class HypoidGearMeshCompoundParametricStudyTool(_4179.AGMAGleasonConicalGearMeshCompoundParametricStudyTool):
    '''HypoidGearMeshCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearMeshCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2057.HypoidGearMesh':
        '''HypoidGearMesh: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2057.HypoidGearMesh)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2057.HypoidGearMesh':
        '''HypoidGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2057.HypoidGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4096.HypoidGearMeshParametricStudyTool]':
        '''List[HypoidGearMeshParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4096.HypoidGearMeshParametricStudyTool))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_4096.HypoidGearMeshParametricStudyTool]':
        '''List[HypoidGearMeshParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4096.HypoidGearMeshParametricStudyTool))
        return value
