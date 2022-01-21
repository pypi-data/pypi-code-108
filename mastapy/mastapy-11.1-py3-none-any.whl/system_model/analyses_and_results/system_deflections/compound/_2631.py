'''_2631.py

CycloidalDiscCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2309
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2473
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2587
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'CycloidalDiscCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscCompoundSystemDeflection',)


class CycloidalDiscCompoundSystemDeflection(_2587.AbstractShaftCompoundSystemDeflection):
    '''CycloidalDiscCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2309.CycloidalDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2473.CycloidalDiscSystemDeflection]':
        '''List[CycloidalDiscSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2473.CycloidalDiscSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2473.CycloidalDiscSystemDeflection]':
        '''List[CycloidalDiscSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2473.CycloidalDiscSystemDeflection))
        return value
