'''_7194.py

KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2279
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7192, _7193, _7191
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7063
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection',)


class KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection(_7191.KlingelnbergCycloPalloidConicalGearSetCompoundAdvancedSystemDeflection):
    '''KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2279.KlingelnbergCycloPalloidHypoidGearSet':
        '''KlingelnbergCycloPalloidHypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2279.KlingelnbergCycloPalloidHypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def klingelnberg_cyclo_palloid_hypoid_gears_compound_advanced_system_deflection(self) -> 'List[_7192.KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection]: 'KlingelnbergCycloPalloidHypoidGearsCompoundAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGearsCompoundAdvancedSystemDeflection, constructor.new(_7192.KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes_compound_advanced_system_deflection(self) -> 'List[_7193.KlingelnbergCycloPalloidHypoidGearMeshCompoundAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshCompoundAdvancedSystemDeflection]: 'KlingelnbergCycloPalloidHypoidMeshesCompoundAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshesCompoundAdvancedSystemDeflection, constructor.new(_7193.KlingelnbergCycloPalloidHypoidGearMeshCompoundAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_7063.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_7063.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_7063.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection]':
        '''List[KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_7063.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection))
        return value
