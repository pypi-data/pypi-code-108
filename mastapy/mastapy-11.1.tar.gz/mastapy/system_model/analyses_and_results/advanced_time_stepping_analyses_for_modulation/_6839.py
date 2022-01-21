'''_6839.py

StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2288
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6683
from mastapy.system_model.analyses_and_results.system_deflections import _2552
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6837, _6838, _6746
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_SET_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation',)


class StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation(_6746.BevelGearSetAdvancedTimeSteppingAnalysisForModulation):
    '''StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_SET_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2288.StraightBevelGearSet':
        '''StraightBevelGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2288.StraightBevelGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6683.StraightBevelGearSetLoadCase':
        '''StraightBevelGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6683.StraightBevelGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2552.StraightBevelGearSetSystemDeflection':
        '''StraightBevelGearSetSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2552.StraightBevelGearSetSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None

    @property
    def straight_bevel_gears_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6837.StraightBevelGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelGearAdvancedTimeSteppingAnalysisForModulation]: 'StraightBevelGearsAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelGearsAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6837.StraightBevelGearAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def straight_bevel_meshes_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6838.StraightBevelGearMeshAdvancedTimeSteppingAnalysisForModulation]':
        '''List[StraightBevelGearMeshAdvancedTimeSteppingAnalysisForModulation]: 'StraightBevelMeshesAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StraightBevelMeshesAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6838.StraightBevelGearMeshAdvancedTimeSteppingAnalysisForModulation))
        return value
