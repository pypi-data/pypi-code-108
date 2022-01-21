'''_7155.py

ConicalGearCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.gears.rating.conical import _498
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7022
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7181
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'ConicalGearCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundAdvancedSystemDeflection',)


class ConicalGearCompoundAdvancedSystemDeflection(_7181.GearCompoundAdvancedSystemDeflection):
    '''ConicalGearCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_duty_cycle_rating(self) -> '_498.ConicalGearDutyCycleRating':
        '''ConicalGearDutyCycleRating: 'GearDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_498.ConicalGearDutyCycleRating)(self.wrapped.GearDutyCycleRating) if self.wrapped.GearDutyCycleRating is not None else None

    @property
    def conical_gear_duty_cycle_rating(self) -> '_498.ConicalGearDutyCycleRating':
        '''ConicalGearDutyCycleRating: 'ConicalGearDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_498.ConicalGearDutyCycleRating)(self.wrapped.ConicalGearDutyCycleRating) if self.wrapped.ConicalGearDutyCycleRating is not None else None

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundAdvancedSystemDeflection]':
        '''List[ConicalGearCompoundAdvancedSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7022.ConicalGearAdvancedSystemDeflection]':
        '''List[ConicalGearAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7022.ConicalGearAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_7022.ConicalGearAdvancedSystemDeflection]':
        '''List[ConicalGearAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7022.ConicalGearAdvancedSystemDeflection))
        return value
