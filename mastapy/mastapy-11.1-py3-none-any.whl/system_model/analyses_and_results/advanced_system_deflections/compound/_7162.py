'''_7162.py

CouplingHalfCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7030
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7200
from mastapy._internal.python_net import python_net_import

_COUPLING_HALF_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'CouplingHalfCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingHalfCompoundAdvancedSystemDeflection',)


class CouplingHalfCompoundAdvancedSystemDeflection(_7200.MountableComponentCompoundAdvancedSystemDeflection):
    '''CouplingHalfCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COUPLING_HALF_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingHalfCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_7030.CouplingHalfAdvancedSystemDeflection]':
        '''List[CouplingHalfAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7030.CouplingHalfAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_7030.CouplingHalfAdvancedSystemDeflection]':
        '''List[CouplingHalfAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7030.CouplingHalfAdvancedSystemDeflection))
        return value
