'''_7056.py

HypoidGearSetAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6624
from mastapy.gears.rating.hypoid import _406
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7054, _7055, _6996
from mastapy.system_model.analyses_and_results.system_deflections import _2499
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'HypoidGearSetAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetAdvancedSystemDeflection',)


class HypoidGearSetAdvancedSystemDeflection(_6996.AGMAGleasonConicalGearSetAdvancedSystemDeflection):
    '''HypoidGearSetAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6624.HypoidGearSetLoadCase':
        '''HypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6624.HypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def rating(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_406.HypoidGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_406.HypoidGearSetRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def hypoid_gears_advanced_system_deflection(self) -> 'List[_7054.HypoidGearAdvancedSystemDeflection]':
        '''List[HypoidGearAdvancedSystemDeflection]: 'HypoidGearsAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsAdvancedSystemDeflection, constructor.new(_7054.HypoidGearAdvancedSystemDeflection))
        return value

    @property
    def hypoid_meshes_advanced_system_deflection(self) -> 'List[_7055.HypoidGearMeshAdvancedSystemDeflection]':
        '''List[HypoidGearMeshAdvancedSystemDeflection]: 'HypoidMeshesAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesAdvancedSystemDeflection, constructor.new(_7055.HypoidGearMeshAdvancedSystemDeflection))
        return value

    @property
    def assembly_system_deflection_results(self) -> 'List[_2499.HypoidGearSetSystemDeflection]':
        '''List[HypoidGearSetSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2499.HypoidGearSetSystemDeflection))
        return value
