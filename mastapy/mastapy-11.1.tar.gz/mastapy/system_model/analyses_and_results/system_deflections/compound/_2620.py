'''_2620.py

ConicalGearSetCompoundSystemDeflection
'''


from typing import List

from mastapy.gears.rating.conical import _501
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2460
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2647
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ConicalGearSetCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetCompoundSystemDeflection',)


class ConicalGearSetCompoundSystemDeflection(_2647.GearSetCompoundSystemDeflection):
    '''ConicalGearSetCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def conical_gear_set_duty_cycle_rating(self) -> '_501.ConicalGearSetDutyCycleRating':
        '''ConicalGearSetDutyCycleRating: 'ConicalGearSetDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_501.ConicalGearSetDutyCycleRating)(self.wrapped.ConicalGearSetDutyCycleRating) if self.wrapped.ConicalGearSetDutyCycleRating is not None else None

    @property
    def assembly_analysis_cases(self) -> 'List[_2460.ConicalGearSetSystemDeflection]':
        '''List[ConicalGearSetSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2460.ConicalGearSetSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2460.ConicalGearSetSystemDeflection]':
        '''List[ConicalGearSetSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2460.ConicalGearSetSystemDeflection))
        return value
