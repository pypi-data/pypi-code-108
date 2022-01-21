'''_2623.py

CouplingCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2466
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2686
from mastapy._internal.python_net import python_net_import

_COUPLING_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'CouplingCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingCompoundSystemDeflection',)


class CouplingCompoundSystemDeflection(_2686.SpecialisedAssemblyCompoundSystemDeflection):
    '''CouplingCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COUPLING_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_2466.CouplingSystemDeflection]':
        '''List[CouplingSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2466.CouplingSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2466.CouplingSystemDeflection]':
        '''List[CouplingSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2466.CouplingSystemDeflection))
        return value
