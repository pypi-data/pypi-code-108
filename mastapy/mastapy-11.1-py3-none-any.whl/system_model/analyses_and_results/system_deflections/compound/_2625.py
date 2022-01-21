'''_2625.py

CouplingHalfCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2465
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2664
from mastapy._internal.python_net import python_net_import

_COUPLING_HALF_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'CouplingHalfCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingHalfCompoundSystemDeflection',)


class CouplingHalfCompoundSystemDeflection(_2664.MountableComponentCompoundSystemDeflection):
    '''CouplingHalfCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _COUPLING_HALF_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingHalfCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_2465.CouplingHalfSystemDeflection]':
        '''List[CouplingHalfSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2465.CouplingHalfSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_2465.CouplingHalfSystemDeflection]':
        '''List[CouplingHalfSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2465.CouplingHalfSystemDeflection))
        return value
