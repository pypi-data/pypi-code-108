'''_2713.py

WormGearSetCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.worm import _341
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2711, _2712, _2647
from mastapy.system_model.analyses_and_results.system_deflections import _2572
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'WormGearSetCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetCompoundSystemDeflection',)


class WormGearSetCompoundSystemDeflection(_2647.GearSetCompoundSystemDeflection):
    '''WormGearSetCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def worm_gear_set_rating(self) -> '_341.WormGearSetDutyCycleRating':
        '''WormGearSetDutyCycleRating: 'WormGearSetRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_341.WormGearSetDutyCycleRating)(self.wrapped.WormGearSetRating) if self.wrapped.WormGearSetRating is not None else None

    @property
    def worm_gears_compound_system_deflection(self) -> 'List[_2711.WormGearCompoundSystemDeflection]':
        '''List[WormGearCompoundSystemDeflection]: 'WormGearsCompoundSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsCompoundSystemDeflection, constructor.new(_2711.WormGearCompoundSystemDeflection))
        return value

    @property
    def worm_meshes_compound_system_deflection(self) -> 'List[_2712.WormGearMeshCompoundSystemDeflection]':
        '''List[WormGearMeshCompoundSystemDeflection]: 'WormMeshesCompoundSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesCompoundSystemDeflection, constructor.new(_2712.WormGearMeshCompoundSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2572.WormGearSetSystemDeflection]':
        '''List[WormGearSetSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2572.WormGearSetSystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2572.WormGearSetSystemDeflection]':
        '''List[WormGearSetSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2572.WormGearSetSystemDeflection))
        return value
