'''_2619.py

ConicalGearMeshCompoundSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2459
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2646
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ConicalGearMeshCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshCompoundSystemDeflection',)


class ConicalGearMeshCompoundSystemDeflection(_2646.GearMeshCompoundSystemDeflection):
    '''ConicalGearMeshCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearMeshCompoundSystemDeflection]':
        '''List[ConicalGearMeshCompoundSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearMeshCompoundSystemDeflection))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_2459.ConicalGearMeshSystemDeflection]':
        '''List[ConicalGearMeshSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2459.ConicalGearMeshSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2459.ConicalGearMeshSystemDeflection]':
        '''List[ConicalGearMeshSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2459.ConicalGearMeshSystemDeflection))
        return value
