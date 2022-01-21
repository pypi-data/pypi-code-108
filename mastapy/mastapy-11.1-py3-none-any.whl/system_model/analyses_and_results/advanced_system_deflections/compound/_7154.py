'''_7154.py

ConceptGearSetCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2262
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7152, _7153, _7183
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7021
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ConceptGearSetCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetCompoundAdvancedSystemDeflection',)


class ConceptGearSetCompoundAdvancedSystemDeflection(_7183.GearSetCompoundAdvancedSystemDeflection):
    '''ConceptGearSetCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2262.ConceptGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2262.ConceptGearSet':
        '''ConceptGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2262.ConceptGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def concept_gears_compound_advanced_system_deflection(self) -> 'List[_7152.ConceptGearCompoundAdvancedSystemDeflection]':
        '''List[ConceptGearCompoundAdvancedSystemDeflection]: 'ConceptGearsCompoundAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGearsCompoundAdvancedSystemDeflection, constructor.new(_7152.ConceptGearCompoundAdvancedSystemDeflection))
        return value

    @property
    def concept_meshes_compound_advanced_system_deflection(self) -> 'List[_7153.ConceptGearMeshCompoundAdvancedSystemDeflection]':
        '''List[ConceptGearMeshCompoundAdvancedSystemDeflection]: 'ConceptMeshesCompoundAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptMeshesCompoundAdvancedSystemDeflection, constructor.new(_7153.ConceptGearMeshCompoundAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_7021.ConceptGearSetAdvancedSystemDeflection]':
        '''List[ConceptGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_7021.ConceptGearSetAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_7021.ConceptGearSetAdvancedSystemDeflection]':
        '''List[ConceptGearSetAdvancedSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_7021.ConceptGearSetAdvancedSystemDeflection))
        return value
