'''_7156.py

ConicalGearMeshCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7023
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7182
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ConicalGearMeshCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundAdvancedSystemDeflection',)


class ConicalGearMeshCompoundAdvancedSystemDeflection(_7182.GearMeshCompoundAdvancedSystemDeflection):
    '''ConicalGearMeshCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundAdvancedSystemDeflection]':
        '''List[ConicalGearMeshCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundAdvancedSystemDeflection))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_7023.ConicalGearMeshAdvancedSystemDeflection]':
        '''List[ConicalGearMeshAdvancedSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_7023.ConicalGearMeshAdvancedSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_7023.ConicalGearMeshAdvancedSystemDeflection]':
        '''List[ConicalGearMeshAdvancedSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_7023.ConicalGearMeshAdvancedSystemDeflection))
        return value
