'''_2591.py

AGMAGleasonConicalGearMeshCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2429
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2619
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'AGMAGleasonConicalGearMeshCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshCompoundSystemDeflection',)


class AGMAGleasonConicalGearMeshCompoundSystemDeflection(_2619.ConicalGearMeshCompoundSystemDeflection):
    '''AGMAGleasonConicalGearMeshCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2429.AGMAGleasonConicalGearMeshSystemDeflection]':
        '''List[AGMAGleasonConicalGearMeshSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2429.AGMAGleasonConicalGearMeshSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2429.AGMAGleasonConicalGearMeshSystemDeflection]':
        '''List[AGMAGleasonConicalGearMeshSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2429.AGMAGleasonConicalGearMeshSystemDeflection))
        return value
