'''_5986.py

FlexiblePinAnalysisConceptLevel
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2493, _2433
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.flexible_pin_analyses import _5985
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_PIN_ANALYSIS_CONCEPT_LEVEL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.FlexiblePinAnalyses', 'FlexiblePinAnalysisConceptLevel')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAnalysisConceptLevel',)


class FlexiblePinAnalysisConceptLevel(_5985.FlexiblePinAnalysis):
    '''FlexiblePinAnalysisConceptLevel

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ANALYSIS_CONCEPT_LEVEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAnalysisConceptLevel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def flexible_pin_nominal_load_case(self) -> '_2493.FlexiblePinAssemblySystemDeflection':
        '''FlexiblePinAssemblySystemDeflection: 'FlexiblePinNominalLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2493.FlexiblePinAssemblySystemDeflection)(self.wrapped.FlexiblePinNominalLoadCase) if self.wrapped.FlexiblePinNominalLoadCase is not None else None

    @property
    def flexible_pin_extreme_load_case(self) -> '_2493.FlexiblePinAssemblySystemDeflection':
        '''FlexiblePinAssemblySystemDeflection: 'FlexiblePinExtremeLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2493.FlexiblePinAssemblySystemDeflection)(self.wrapped.FlexiblePinExtremeLoadCase) if self.wrapped.FlexiblePinExtremeLoadCase is not None else None

    @property
    def planet_bearings_in_nominal_load(self) -> 'List[_2433.BearingSystemDeflection]':
        '''List[BearingSystemDeflection]: 'PlanetBearingsInNominalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetBearingsInNominalLoad, constructor.new(_2433.BearingSystemDeflection))
        return value
