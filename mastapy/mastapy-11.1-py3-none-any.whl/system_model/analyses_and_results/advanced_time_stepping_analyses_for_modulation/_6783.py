'''_6783.py

FaceGearSetAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6601
from mastapy.system_model.analyses_and_results.system_deflections import _2490
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6781, _6782, _6788
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'FaceGearSetAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetAdvancedTimeSteppingAnalysisForModulation',)


class FaceGearSetAdvancedTimeSteppingAnalysisForModulation(_6788.GearSetAdvancedTimeSteppingAnalysisForModulation):
    '''FaceGearSetAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2269.FaceGearSet':
        '''FaceGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2269.FaceGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6601.FaceGearSetLoadCase':
        '''FaceGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6601.FaceGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2490.FaceGearSetSystemDeflection':
        '''FaceGearSetSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2490.FaceGearSetSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None

    @property
    def face_gears_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6781.FaceGearAdvancedTimeSteppingAnalysisForModulation]':
        '''List[FaceGearAdvancedTimeSteppingAnalysisForModulation]: 'FaceGearsAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6781.FaceGearAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def face_meshes_advanced_time_stepping_analysis_for_modulation(self) -> 'List[_6782.FaceGearMeshAdvancedTimeSteppingAnalysisForModulation]':
        '''List[FaceGearMeshAdvancedTimeSteppingAnalysisForModulation]: 'FaceMeshesAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesAdvancedTimeSteppingAnalysisForModulation, constructor.new(_6782.FaceGearMeshAdvancedTimeSteppingAnalysisForModulation))
        return value
