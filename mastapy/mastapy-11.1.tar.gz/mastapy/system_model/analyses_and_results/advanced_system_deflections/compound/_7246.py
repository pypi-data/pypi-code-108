'''_7246.py

WormGearCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.gears.rating.worm import _338
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.gears import _2291
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7117
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7181
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'WormGearCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearCompoundAdvancedSystemDeflection',)


class WormGearCompoundAdvancedSystemDeflection(_7181.GearCompoundAdvancedSystemDeflection):
    '''WormGearCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearCompoundAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_duty_cycle_rating(self) -> '_338.WormGearDutyCycleRating':
        '''WormGearDutyCycleRating: 'GearDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_338.WormGearDutyCycleRating)(self.wrapped.GearDutyCycleRating) if self.wrapped.GearDutyCycleRating is not None else None

    @property
    def worm_gear_duty_cycle_rating(self) -> '_338.WormGearDutyCycleRating':
        '''WormGearDutyCycleRating: 'WormGearDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_338.WormGearDutyCycleRating)(self.wrapped.WormGearDutyCycleRating) if self.wrapped.WormGearDutyCycleRating is not None else None

    @property
    def component_design(self) -> '_2291.WormGear':
        '''WormGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2291.WormGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_7117.WormGearAdvancedSystemDeflection]':
        '''List[WormGearAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7117.WormGearAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7117.WormGearAdvancedSystemDeflection]':
        '''List[WormGearAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7117.WormGearAdvancedSystemDeflection))
        return value
