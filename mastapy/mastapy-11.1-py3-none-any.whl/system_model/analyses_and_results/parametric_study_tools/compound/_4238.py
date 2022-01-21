'''_4238.py

HypoidGearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4236, _4237, _4180
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4098
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'HypoidGearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundParametricStudyTool',)


class HypoidGearSetCompoundParametricStudyTool(_4180.AGMAGleasonConicalGearSetCompoundParametricStudyTool):
    '''HypoidGearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def hypoid_gears_compound_parametric_study_tool(self) -> 'List[_4236.HypoidGearCompoundParametricStudyTool]':
        '''List[HypoidGearCompoundParametricStudyTool]: 'HypoidGearsCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundParametricStudyTool, constructor.new(_4236.HypoidGearCompoundParametricStudyTool))
        return value

    @property
    def hypoid_meshes_compound_parametric_study_tool(self) -> 'List[_4237.HypoidGearMeshCompoundParametricStudyTool]':
        '''List[HypoidGearMeshCompoundParametricStudyTool]: 'HypoidMeshesCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundParametricStudyTool, constructor.new(_4237.HypoidGearMeshCompoundParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4098.HypoidGearSetParametricStudyTool]':
        '''List[HypoidGearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4098.HypoidGearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4098.HypoidGearSetParametricStudyTool]':
        '''List[HypoidGearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4098.HypoidGearSetParametricStudyTool))
        return value
