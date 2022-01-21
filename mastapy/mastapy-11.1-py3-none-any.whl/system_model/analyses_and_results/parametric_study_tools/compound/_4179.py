'''_4179.py

AGMAGleasonConicalGearMeshCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4031
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4207
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'AGMAGleasonConicalGearMeshCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundParametricStudyTool',)


class AGMAGleasonConicalGearMeshCompoundParametricStudyTool(_4207.ConicalGearMeshCompoundParametricStudyTool):
    '''AGMAGleasonConicalGearMeshCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4031.AGMAGleasonConicalGearMeshParametricStudyTool]':
        '''List[AGMAGleasonConicalGearMeshParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4031.AGMAGleasonConicalGearMeshParametricStudyTool))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4031.AGMAGleasonConicalGearMeshParametricStudyTool]':
        '''List[AGMAGleasonConicalGearMeshParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4031.AGMAGleasonConicalGearMeshParametricStudyTool))
        return value
