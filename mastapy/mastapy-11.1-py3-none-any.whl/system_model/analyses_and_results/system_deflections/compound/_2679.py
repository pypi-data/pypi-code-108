'''_2679.py

RollingRingCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2336
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2534
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2625
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'RollingRingCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingCompoundSystemDeflection',)


class RollingRingCompoundSystemDeflection(_2625.CouplingHalfCompoundSystemDeflection):
    '''RollingRingCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2336.RollingRing':
        '''RollingRing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2336.RollingRing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2534.RollingRingSystemDeflection]':
        '''List[RollingRingSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2534.RollingRingSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[RollingRingCompoundSystemDeflection]':
        '''List[RollingRingCompoundSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingCompoundSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2534.RollingRingSystemDeflection]':
        '''List[RollingRingSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2534.RollingRingSystemDeflection))
        return value
