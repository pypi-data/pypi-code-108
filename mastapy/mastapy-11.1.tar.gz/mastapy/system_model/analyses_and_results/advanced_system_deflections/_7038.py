'''_7038.py

CylindricalGearAdvancedSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _969, _996
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.gears import _2265, _2267
from mastapy.system_model.analyses_and_results.static_loads import _6575, _6580
from mastapy.gears.rating.cylindrical import _423
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7039, _7041, _7050
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'CylindricalGearAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearAdvancedSystemDeflection',)


class CylindricalGearAdvancedSystemDeflection(_7050.GearAdvancedSystemDeflection):
    '''CylindricalGearAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_von_mises_root_stress_tension(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressTension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressTension

    @property
    def maximum_principal_root_stress_tension(self) -> 'float':
        '''float: 'MaximumPrincipalRootStressTension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalRootStressTension

    @property
    def maximum_von_mises_root_stress_compression(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressCompression' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressCompression

    @property
    def maximum_principal_root_stress_compression(self) -> 'float':
        '''float: 'MaximumPrincipalRootStressCompression' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalRootStressCompression

    @property
    def gear_design(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'GearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.GearDesign.__class__.__mro__:
            raise CastException('Failed to cast gear_design to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.GearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDesign.__class__)(self.wrapped.GearDesign) if self.wrapped.GearDesign is not None else None

    @property
    def component_design(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6575.CylindricalGearLoadCase':
        '''CylindricalGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6575.CylindricalGearLoadCase.TYPE not in self.wrapped.ComponentLoadCase.__class__.__mro__:
            raise CastException('Failed to cast component_load_case to CylindricalGearLoadCase. Expected: {}.'.format(self.wrapped.ComponentLoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentLoadCase.__class__)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_detailed_analysis(self) -> '_423.CylindricalGearRating':
        '''CylindricalGearRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_423.CylindricalGearRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def cylindrical_gear_advanced_system_deflection_meshes(self) -> 'List[_7039.CylindricalGearMeshAdvancedSystemDeflection]':
        '''List[CylindricalGearMeshAdvancedSystemDeflection]: 'CylindricalGearAdvancedSystemDeflectionMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearAdvancedSystemDeflectionMeshes, constructor.new(_7039.CylindricalGearMeshAdvancedSystemDeflection))
        return value

    @property
    def cylindrical_meshed_gear_advanced_system_deflections(self) -> 'List[_7041.CylindricalMeshedGearAdvancedSystemDeflection]':
        '''List[CylindricalMeshedGearAdvancedSystemDeflection]: 'CylindricalMeshedGearAdvancedSystemDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshedGearAdvancedSystemDeflections, constructor.new(_7041.CylindricalMeshedGearAdvancedSystemDeflection))
        return value

    @property
    def cylindrical_gear_advanced_system_deflections_in_meshes(self) -> 'List[_7041.CylindricalMeshedGearAdvancedSystemDeflection]':
        '''List[CylindricalMeshedGearAdvancedSystemDeflection]: 'CylindricalGearAdvancedSystemDeflectionsInMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearAdvancedSystemDeflectionsInMeshes, constructor.new(_7041.CylindricalMeshedGearAdvancedSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[CylindricalGearAdvancedSystemDeflection]':
        '''List[CylindricalGearAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(CylindricalGearAdvancedSystemDeflection))
        return value
