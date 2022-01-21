'''_7146.py

ClutchHalfCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2319
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7013
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7162
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ClutchHalfCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalfCompoundAdvancedSystemDeflection',)


class ClutchHalfCompoundAdvancedSystemDeflection(_7162.CouplingHalfCompoundAdvancedSystemDeflection):
    '''ClutchHalfCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalfCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2319.ClutchHalf':
        '''ClutchHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2319.ClutchHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7013.ClutchHalfAdvancedSystemDeflection]':
        '''List[ClutchHalfAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7013.ClutchHalfAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7013.ClutchHalfAdvancedSystemDeflection]':
        '''List[ClutchHalfAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7013.ClutchHalfAdvancedSystemDeflection))
        return value
