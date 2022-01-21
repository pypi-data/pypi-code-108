'''_2594.py

BearingCompoundSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import _2182
from mastapy.bearings.bearing_results import _1702, _1710, _1713
from mastapy._internal.cast_exception import CastException
from mastapy.bearings.bearing_results.rolling import (
    _1741, _1748, _1756, _1772,
    _1796
)
from mastapy.system_model.analyses_and_results.system_deflections import _2433
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2622
from mastapy._internal.python_net import python_net_import

_BEARING_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'BearingCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingCompoundSystemDeflection',)


class BearingCompoundSystemDeflection(_2622.ConnectorCompoundSystemDeflection):
    '''BearingCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEARING_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_element_stress_for_iso2812007_dynamic_equivalent_load(self) -> 'float':
        '''float: 'MaximumElementStressForISO2812007DynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumElementStressForISO2812007DynamicEquivalentLoad

    @property
    def maximum_element_stress_for_isots162812008_dynamic_equivalent_load(self) -> 'float':
        '''float: 'MaximumElementStressForISOTS162812008DynamicEquivalentLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumElementStressForISOTS162812008DynamicEquivalentLoad

    @property
    def component_design(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2182.Bearing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_detailed_analysis(self) -> '_1702.LoadedBearingDutyCycle':
        '''LoadedBearingDutyCycle: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1702.LoadedBearingDutyCycle.TYPE not in self.wrapped.ComponentDetailedAnalysis.__class__.__mro__:
            raise CastException('Failed to cast component_detailed_analysis to LoadedBearingDutyCycle. Expected: {}.'.format(self.wrapped.ComponentDetailedAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDetailedAnalysis.__class__)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2433.BearingSystemDeflection]':
        '''List[BearingSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2433.BearingSystemDeflection))
        return value

    @property
    def planetaries(self) -> 'List[BearingCompoundSystemDeflection]':
        '''List[BearingCompoundSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(BearingCompoundSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2433.BearingSystemDeflection]':
        '''List[BearingSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2433.BearingSystemDeflection))
        return value
