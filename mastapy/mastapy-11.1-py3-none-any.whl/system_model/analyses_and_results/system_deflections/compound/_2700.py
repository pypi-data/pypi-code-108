'''_2700.py

StraightBevelSunGearCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2555
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2693
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_SUN_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'StraightBevelSunGearCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelSunGearCompoundSystemDeflection',)


class StraightBevelSunGearCompoundSystemDeflection(_2693.StraightBevelDiffGearCompoundSystemDeflection):
    '''StraightBevelSunGearCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_SUN_GEAR_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelSunGearCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases_ready(self) -> 'List[_2555.StraightBevelSunGearSystemDeflection]':
        '''List[StraightBevelSunGearSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2555.StraightBevelSunGearSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2555.StraightBevelSunGearSystemDeflection]':
        '''List[StraightBevelSunGearSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2555.StraightBevelSunGearSystemDeflection))
        return value
