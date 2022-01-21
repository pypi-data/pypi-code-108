'''_7047.py

FaceGearSetAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2269
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6601
from mastapy.gears.rating.face import _416
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7045, _7046, _7052
from mastapy.system_model.analyses_and_results.system_deflections import _2490
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'FaceGearSetAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetAdvancedSystemDeflection',)


class FaceGearSetAdvancedSystemDeflection(_7052.GearSetAdvancedSystemDeflection):
    '''FaceGearSetAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetAdvancedSystemDeflection.TYPE'):
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
    def rating(self) -> '_416.FaceGearSetRating':
        '''FaceGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_416.FaceGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_416.FaceGearSetRating':
        '''FaceGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_416.FaceGearSetRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def face_gears_advanced_system_deflection(self) -> 'List[_7045.FaceGearAdvancedSystemDeflection]':
        '''List[FaceGearAdvancedSystemDeflection]: 'FaceGearsAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearsAdvancedSystemDeflection, constructor.new(_7045.FaceGearAdvancedSystemDeflection))
        return value

    @property
    def face_meshes_advanced_system_deflection(self) -> 'List[_7046.FaceGearMeshAdvancedSystemDeflection]':
        '''List[FaceGearMeshAdvancedSystemDeflection]: 'FaceMeshesAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceMeshesAdvancedSystemDeflection, constructor.new(_7046.FaceGearMeshAdvancedSystemDeflection))
        return value

    @property
    def assembly_system_deflection_results(self) -> 'List[_2490.FaceGearSetSystemDeflection]':
        '''List[FaceGearSetSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2490.FaceGearSetSystemDeflection))
        return value
