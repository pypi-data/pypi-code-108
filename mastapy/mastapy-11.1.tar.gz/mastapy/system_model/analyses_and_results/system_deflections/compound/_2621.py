'''_2621.py

ConnectionCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2462
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7256
from mastapy._internal.python_net import python_net_import

_CONNECTION_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ConnectionCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionCompoundSystemDeflection',)


class ConnectionCompoundSystemDeflection(_7256.ConnectionCompoundAnalysis):
    '''ConnectionCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_2462.ConnectionSystemDeflection]':
        '''List[ConnectionSystemDeflection]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_2462.ConnectionSystemDeflection))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_2462.ConnectionSystemDeflection]':
        '''List[ConnectionSystemDeflection]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_2462.ConnectionSystemDeflection))
        return value
