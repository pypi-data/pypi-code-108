'''_7003.py

BevelDifferentialGearSetAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2256
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6539
from mastapy.gears.rating.bevel import _516
from mastapy.gears.rating.zerol_bevel import _337
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.straight_bevel import _367
from mastapy.gears.rating.spiral_bevel import _370
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7001, _7002, _7008
from mastapy.system_model.analyses_and_results.system_deflections import _2437
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'BevelDifferentialGearSetAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearSetAdvancedSystemDeflection',)


class BevelDifferentialGearSetAdvancedSystemDeflection(_7008.BevelGearSetAdvancedSystemDeflection):
    '''BevelDifferentialGearSetAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearSetAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2256.BevelDifferentialGearSet':
        '''BevelDifferentialGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2256.BevelDifferentialGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6539.BevelDifferentialGearSetLoadCase':
        '''BevelDifferentialGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6539.BevelDifferentialGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def rating(self) -> '_516.BevelGearSetRating':
        '''BevelGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _516.BevelGearSetRating.TYPE not in self.wrapped.Rating.__class__.__mro__:
            raise CastException('Failed to cast rating to BevelGearSetRating. Expected: {}.'.format(self.wrapped.Rating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Rating.__class__)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def rating_of_type_zerol_bevel_gear_set_rating(self) -> '_337.ZerolBevelGearSetRating':
        '''ZerolBevelGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _337.ZerolBevelGearSetRating.TYPE not in self.wrapped.Rating.__class__.__mro__:
            raise CastException('Failed to cast rating to ZerolBevelGearSetRating. Expected: {}.'.format(self.wrapped.Rating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Rating.__class__)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def rating_of_type_straight_bevel_gear_set_rating(self) -> '_367.StraightBevelGearSetRating':
        '''StraightBevelGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _367.StraightBevelGearSetRating.TYPE not in self.wrapped.Rating.__class__.__mro__:
            raise CastException('Failed to cast rating to StraightBevelGearSetRating. Expected: {}.'.format(self.wrapped.Rating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Rating.__class__)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def rating_of_type_spiral_bevel_gear_set_rating(self) -> '_370.SpiralBevelGearSetRating':
        '''SpiralBevelGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _370.SpiralBevelGearSetRating.TYPE not in self.wrapped.Rating.__class__.__mro__:
            raise CastException('Failed to cast rating to SpiralBevelGearSetRating. Expected: {}.'.format(self.wrapped.Rating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Rating.__class__)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_516.BevelGearSetRating':
        '''BevelGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _516.BevelGearSetRating.TYPE not in self.wrapped.ComponentDetailedAnalysis.__class__.__mro__:
            raise CastException('Failed to cast component_detailed_analysis to BevelGearSetRating. Expected: {}.'.format(self.wrapped.ComponentDetailedAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDetailedAnalysis.__class__)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def component_detailed_analysis_of_type_zerol_bevel_gear_set_rating(self) -> '_337.ZerolBevelGearSetRating':
        '''ZerolBevelGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _337.ZerolBevelGearSetRating.TYPE not in self.wrapped.ComponentDetailedAnalysis.__class__.__mro__:
            raise CastException('Failed to cast component_detailed_analysis to ZerolBevelGearSetRating. Expected: {}.'.format(self.wrapped.ComponentDetailedAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDetailedAnalysis.__class__)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def component_detailed_analysis_of_type_straight_bevel_gear_set_rating(self) -> '_367.StraightBevelGearSetRating':
        '''StraightBevelGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _367.StraightBevelGearSetRating.TYPE not in self.wrapped.ComponentDetailedAnalysis.__class__.__mro__:
            raise CastException('Failed to cast component_detailed_analysis to StraightBevelGearSetRating. Expected: {}.'.format(self.wrapped.ComponentDetailedAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDetailedAnalysis.__class__)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def component_detailed_analysis_of_type_spiral_bevel_gear_set_rating(self) -> '_370.SpiralBevelGearSetRating':
        '''SpiralBevelGearSetRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _370.SpiralBevelGearSetRating.TYPE not in self.wrapped.ComponentDetailedAnalysis.__class__.__mro__:
            raise CastException('Failed to cast component_detailed_analysis to SpiralBevelGearSetRating. Expected: {}.'.format(self.wrapped.ComponentDetailedAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDetailedAnalysis.__class__)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def bevel_differential_gears_advanced_system_deflection(self) -> 'List[_7001.BevelDifferentialGearAdvancedSystemDeflection]':
        '''List[BevelDifferentialGearAdvancedSystemDeflection]: 'BevelDifferentialGearsAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialGearsAdvancedSystemDeflection, constructor.new(_7001.BevelDifferentialGearAdvancedSystemDeflection))
        return value

    @property
    def bevel_differential_meshes_advanced_system_deflection(self) -> 'List[_7002.BevelDifferentialGearMeshAdvancedSystemDeflection]':
        '''List[BevelDifferentialGearMeshAdvancedSystemDeflection]: 'BevelDifferentialMeshesAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BevelDifferentialMeshesAdvancedSystemDeflection, constructor.new(_7002.BevelDifferentialGearMeshAdvancedSystemDeflection))
        return value

    @property
    def assembly_system_deflection_results(self) -> 'List[_2437.BevelDifferentialGearSetSystemDeflection]':
        '''List[BevelDifferentialGearSetSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2437.BevelDifferentialGearSetSystemDeflection))
        return value
