'''_4302.py

ZerolBevelGearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2294
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4300, _4301, _4192
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4173
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'ZerolBevelGearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearSetCompoundParametricStudyTool',)


class ZerolBevelGearSetCompoundParametricStudyTool(_4192.BevelGearSetCompoundParametricStudyTool):
    '''ZerolBevelGearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2294.ZerolBevelGearSet':
        '''ZerolBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2294.ZerolBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def zerol_bevel_gears_compound_parametric_study_tool(self) -> 'List[_4300.ZerolBevelGearCompoundParametricStudyTool]':
        '''List[ZerolBevelGearCompoundParametricStudyTool]: 'ZerolBevelGearsCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelGearsCompoundParametricStudyTool, constructor.new(_4300.ZerolBevelGearCompoundParametricStudyTool))
        return value

    @property
    def zerol_bevel_meshes_compound_parametric_study_tool(self) -> 'List[_4301.ZerolBevelGearMeshCompoundParametricStudyTool]':
        '''List[ZerolBevelGearMeshCompoundParametricStudyTool]: 'ZerolBevelMeshesCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ZerolBevelMeshesCompoundParametricStudyTool, constructor.new(_4301.ZerolBevelGearMeshCompoundParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4173.ZerolBevelGearSetParametricStudyTool]':
        '''List[ZerolBevelGearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4173.ZerolBevelGearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4173.ZerolBevelGearSetParametricStudyTool]':
        '''List[ZerolBevelGearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4173.ZerolBevelGearSetParametricStudyTool))
        return value
