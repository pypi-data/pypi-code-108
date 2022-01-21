'''_4187.py

BevelDifferentialGearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4185, _4186, _4192
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4040
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'BevelDifferentialGearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetCompoundParametricStudyTool',)


class BevelDifferentialGearSetCompoundParametricStudyTool(_4192.BevelGearSetCompoundParametricStudyTool):
    '''BevelDifferentialGearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def bevel_differential_gears_compound_parametric_study_tool(self) -> 'List[_4185.BevelDifferentialGearCompoundParametricStudyTool]':
        '''List[BevelDifferentialGearCompoundParametricStudyTool]: 'BevelDifferentialGearsCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsCompoundParametricStudyTool, constructor.new(_4185.BevelDifferentialGearCompoundParametricStudyTool))
        return value

    @property
    def bevel_differential_meshes_compound_parametric_study_tool(self) -> 'List[_4186.BevelDifferentialGearMeshCompoundParametricStudyTool]':
        '''List[BevelDifferentialGearMeshCompoundParametricStudyTool]: 'BevelDifferentialMeshesCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesCompoundParametricStudyTool, constructor.new(_4186.BevelDifferentialGearMeshCompoundParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4040.BevelDifferentialGearSetParametricStudyTool]':
        '''List[BevelDifferentialGearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4040.BevelDifferentialGearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4040.BevelDifferentialGearSetParametricStudyTool]':
        '''List[BevelDifferentialGearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4040.BevelDifferentialGearSetParametricStudyTool))
        return value
