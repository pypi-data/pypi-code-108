'''_2586.py

AbstractAssemblyCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2425
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2666
from mastapy._internal.python_net import python_net_import

_ABSTRACT_ASSEMBLY_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'AbstractAssemblyCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractAssemblyCompoundSystemDeflection',)


class AbstractAssemblyCompoundSystemDeflection(_2666.PartCompoundSystemDeflection):
    '''AbstractAssemblyCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_ASSEMBLY_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractAssemblyCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_2425.AbstractAssemblySystemDeflection]':
        '''List[AbstractAssemblySystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2425.AbstractAssemblySystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2425.AbstractAssemblySystemDeflection]':
        '''List[AbstractAssemblySystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2425.AbstractAssemblySystemDeflection))
        return value
