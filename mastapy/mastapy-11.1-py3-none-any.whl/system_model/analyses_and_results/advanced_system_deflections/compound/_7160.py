'''_7160.py

CouplingCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7028
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7221
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'CouplingCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundAdvancedSystemDeflection',)


class CouplingCompoundAdvancedSystemDeflection(_7221.SpecialisedAssemblyCompoundAdvancedSystemDeflection):
    '''CouplingCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_7028.CouplingAdvancedSystemDeflection]':
        '''List[CouplingAdvancedSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_7028.CouplingAdvancedSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_7028.CouplingAdvancedSystemDeflection]':
        '''List[CouplingAdvancedSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_7028.CouplingAdvancedSystemDeflection))
        return value
