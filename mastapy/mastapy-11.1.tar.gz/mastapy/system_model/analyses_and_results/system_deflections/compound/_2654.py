'''_2654.py

KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2503
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2619
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection',)


class KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection(_2619.ConicalGearMeshCompoundSystemDeflection):
    '''KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection]':
        '''List[KlingelnbergCycloPalloidConicalGearMeshSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2503.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection))
        return value
