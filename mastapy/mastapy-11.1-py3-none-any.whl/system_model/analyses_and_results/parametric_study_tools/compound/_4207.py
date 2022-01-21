'''_4207.py

ConicalGearMeshCompoundParametricStudyTool
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4059
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4233
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ConicalGearMeshCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundParametricStudyTool',)


class ConicalGearMeshCompoundParametricStudyTool(_4233.GearMeshCompoundParametricStudyTool):
    '''ConicalGearMeshCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundParametricStudyTool]':
        '''List[ConicalGearMeshCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundParametricStudyTool))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_4059.ConicalGearMeshParametricStudyTool]':
        '''List[ConicalGearMeshParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4059.ConicalGearMeshParametricStudyTool))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4059.ConicalGearMeshParametricStudyTool]':
        '''List[ConicalGearMeshParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4059.ConicalGearMeshParametricStudyTool))
        return value
