'''_7201.py

OilSealCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2207
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7071
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7159
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'OilSealCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealCompoundAdvancedSystemDeflection',)


class OilSealCompoundAdvancedSystemDeflection(_7159.ConnectorCompoundAdvancedSystemDeflection):
    '''OilSealCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2207.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7071.OilSealAdvancedSystemDeflection]':
        '''List[OilSealAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7071.OilSealAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7071.OilSealAdvancedSystemDeflection]':
        '''List[OilSealAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7071.OilSealAdvancedSystemDeflection))
        return value
