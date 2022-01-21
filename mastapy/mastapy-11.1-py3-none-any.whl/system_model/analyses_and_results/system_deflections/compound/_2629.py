'''_2629.py

CycloidalAssemblyCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2308
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2470
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2686
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_ASSEMBLY_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'CycloidalAssemblyCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalAssemblyCompoundSystemDeflection',)


class CycloidalAssemblyCompoundSystemDeflection(_2686.SpecialisedAssemblyCompoundSystemDeflection):
    '''CycloidalAssemblyCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_ASSEMBLY_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalAssemblyCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2308.CycloidalAssembly':
        '''CycloidalAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2308.CycloidalAssembly)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2308.CycloidalAssembly':
        '''CycloidalAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2308.CycloidalAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2470.CycloidalAssemblySystemDeflection]':
        '''List[CycloidalAssemblySystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2470.CycloidalAssemblySystemDeflection))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_2470.CycloidalAssemblySystemDeflection]':
        '''List[CycloidalAssemblySystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2470.CycloidalAssemblySystemDeflection))
        return value
