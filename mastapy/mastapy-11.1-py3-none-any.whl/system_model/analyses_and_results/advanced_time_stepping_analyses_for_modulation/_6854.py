'''_6854.py

WormGearSetAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6703
from mastapy.system_model.analyses_and_results.system_deflections import _2572
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6852, _6853, _6788
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'WormGearSetAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetAdvancedTimeSteppingAnalysisForModulation',)


class WormGearSetAdvancedTimeSteppingAnalysisForModulation(_6788.GearSetAdvancedTimeSteppingAnalysisForModulation):
    '''WormGearSetAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetAdvancedTimeSteppingAnalysisForModulation.TYPE'):
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
    def system_deflection_results(self) -> '_2572.WormGearSetSystemDeflection':
        '''WormGearSetSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2572.WormGearSetSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None

    @property
    def worm_gears_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6852.WormGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearAdvancedTimeSteppingAnalysisForModulation]: 'WormGearsAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6852.WormGearAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def worm_meshes_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6853.WormGearMeshAdvancedTimeSteppingAnalysisForModulation]':
        '''List[WormGearMeshAdvancedTimeSteppingAnalysisForModulation]: 'WormMeshesAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6853.WormGearMeshAdvancedTimeSteppingAnalysisForModulation))
        return value
