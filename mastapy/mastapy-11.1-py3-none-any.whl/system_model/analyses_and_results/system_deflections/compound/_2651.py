'''_2651.py

HypoidGearSetCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2275
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2649, _2650, _2592
from mastapy.system_model.analyses_and_results.system_deflections import _2499
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'HypoidGearSetCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetCompoundSystemDeflection',)


class HypoidGearSetCompoundSystemDeflection(_2592.AGMAGleasonConicalGearSetCompoundSystemDeflection):
    '''HypoidGearSetCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2275.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2275.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def hypoid_gears_compound_system_deflection(self) -> 'List[_2649.HypoidGearCompoundSystemDeflection]':
        '''List[HypoidGearCompoundSystemDeflection]: 'HypoidGearsCompoundSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsCompoundSystemDeflection, constructor.new(_2649.HypoidGearCompoundSystemDeflection))
        return value

    @property
    def hypoid_meshes_compound_system_deflection(self) -> 'List[_2650.HypoidGearMeshCompoundSystemDeflection]':
        '''List[HypoidGearMeshCompoundSystemDeflection]: 'HypoidMeshesCompoundSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesCompoundSystemDeflection, constructor.new(_2650.HypoidGearMeshCompoundSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2499.HypoidGearSetSystemDeflection]':
        '''List[HypoidGearSetSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2499.HypoidGearSetSystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2499.HypoidGearSetSystemDeflection]':
        '''List[HypoidGearSetSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2499.HypoidGearSetSystemDeflection))
        return value
