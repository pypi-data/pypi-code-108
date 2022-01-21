'''_4248.py

KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2281
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4246, _4247, _4242
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4108
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool',)


class KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool(_4242.KlingelnbergCycloPalloidConicalGearSetCompoundParametricStudyTool):
    '''KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2281.KlingelnbergCycloPalloidSpiralBevelGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2281.KlingelnbergCycloPalloidSpiralBevelGearSet':
        '''KlingelnbergCycloPalloidSpiralBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2281.KlingelnbergCycloPalloidSpiralBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gears_compound_parametric_study_tool(self) -> 'List[_4246.KlingelnbergCycloPalloidSpiralBevelGearCompoundParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearCompoundParametricStudyTool]: 'KlingelnbergCycloPalloidSpiralBevelGearsCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearsCompoundParametricStudyTool, constructor.new(_4246.KlingelnbergCycloPalloidSpiralBevelGearCompoundParametricStudyTool))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshes_compound_parametric_study_tool(self) -> 'List[_4247.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundParametricStudyTool]: 'KlingelnbergCycloPalloidSpiralBevelMeshesCompoundParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshesCompoundParametricStudyTool, constructor.new(_4247.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4108.KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4108.KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4108.KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4108.KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool))
        return value
