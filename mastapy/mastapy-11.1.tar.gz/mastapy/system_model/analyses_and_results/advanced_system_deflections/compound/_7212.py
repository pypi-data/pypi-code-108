'''_7212.py

RingPinsCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7082
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7200
from mastapy._internal.python_net import python_net_import

_RING_PINS_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'RingPinsCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsCompoundAdvancedSystemDeflection',)


class RingPinsCompoundAdvancedSystemDeflection(_7200.MountableComponentCompoundAdvancedSystemDeflection):
    '''RingPinsCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7082.RingPinsAdvancedSystemDeflection]':
        '''List[RingPinsAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7082.RingPinsAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7082.RingPinsAdvancedSystemDeflection]':
        '''List[RingPinsAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7082.RingPinsAdvancedSystemDeflection))
        return value
