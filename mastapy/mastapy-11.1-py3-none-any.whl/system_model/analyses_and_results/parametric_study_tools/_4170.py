'''_4170.py

WormGearSetParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6703
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4169, _4168, _4094
from mastapy.system_model.analyses_and_results.system_deflections import _2572
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'WormGearSetParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetParametricStudyTool',)


class WormGearSetParametricStudyTool(_4094.GearSetParametricStudyTool):
    '''WormGearSetParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6703.WormGearSetLoadCase':
        '''WormGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6703.WormGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def worm_gears_parametric_study_tool(self) -> 'List[_4169.WormGearParametricStudyTool]':
        '''List[WormGearParametricStudyTool]: 'WormGearsParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsParametricStudyTool, constructor.new(_4169.WormGearParametricStudyTool))
        return value

    @property
    def worm_meshes_parametric_study_tool(self) -> 'List[_4168.WormGearMeshParametricStudyTool]':
        '''List[WormGearMeshParametricStudyTool]: 'WormMeshesParametricStudyTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesParametricStudyTool, constructor.new(_4168.WormGearMeshParametricStudyTool))
        return value

    @property
    def assembly_system_deflection_results(self) -> 'List[_2572.WormGearSetSystemDeflection]':
        '''List[WormGearSetSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2572.WormGearSetSystemDeflection))
        return value
