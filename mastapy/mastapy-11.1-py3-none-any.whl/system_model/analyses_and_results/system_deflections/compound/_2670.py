'''_2670.py

PlanetaryConnectionCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.connections_and_sockets import _2029
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2524
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2685
from mastapy._internal.python_net import python_net_import

_PLANETARY_CONNECTION_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'PlanetaryConnectionCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryConnectionCompoundSystemDeflection',)


class PlanetaryConnectionCompoundSystemDeflection(_2685.ShaftToMountableComponentConnectionCompoundSystemDeflection):
    '''PlanetaryConnectionCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_CONNECTION_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryConnectionCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2029.PlanetaryConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2029.PlanetaryConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2524.PlanetaryConnectionSystemDeflection]':
        '''List[PlanetaryConnectionSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2524.PlanetaryConnectionSystemDeflection))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_2524.PlanetaryConnectionSystemDeflection]':
        '''List[PlanetaryConnectionSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2524.PlanetaryConnectionSystemDeflection))
        return value
