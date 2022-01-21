'''_2646.py

GearMeshCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2494
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2652
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'GearMeshCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshCompoundSystemDeflection',)


class GearMeshCompoundSystemDeflection(_2652.InterMountableComponentConnectionCompoundSystemDeflection):
    '''GearMeshCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2494.GearMeshSystemDeflection]':
        '''List[GearMeshSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2494.GearMeshSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2494.GearMeshSystemDeflection]':
        '''List[GearMeshSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2494.GearMeshSystemDeflection))
        return value
