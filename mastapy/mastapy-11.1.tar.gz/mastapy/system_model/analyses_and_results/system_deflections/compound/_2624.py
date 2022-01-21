'''_2624.py

CouplingConnectionCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2464
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2652
from mastapy._internal.python_net import python_net_import

_COUPLING_CONNECTION_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'CouplingConnectionCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingConnectionCompoundSystemDeflection',)


class CouplingConnectionCompoundSystemDeflection(_2652.InterMountableComponentConnectionCompoundSystemDeflection):
    '''CouplingConnectionCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COUPLING_CONNECTION_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingConnectionCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2464.CouplingConnectionSystemDeflection]':
        '''List[CouplingConnectionSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2464.CouplingConnectionSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2464.CouplingConnectionSystemDeflection]':
        '''List[CouplingConnectionSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2464.CouplingConnectionSystemDeflection))
        return value
