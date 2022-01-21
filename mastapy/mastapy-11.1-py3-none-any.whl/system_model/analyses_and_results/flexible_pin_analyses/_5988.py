'''_5988.py

FlexiblePinAnalysisGearAndBearingRating
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections.compound import _2635, _2671, _2594
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.flexible_pin_analyses import _5985
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_PIN_ANALYSIS_GEAR_AND_BEARING_RATING = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.FlexiblePinAnalyses', 'FlexiblePinAnalysisGearAndBearingRating')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAnalysisGearAndBearingRating',)


class FlexiblePinAnalysisGearAndBearingRating(_5985.FlexiblePinAnalysis):
    '''FlexiblePinAnalysisGearAndBearingRating

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ANALYSIS_GEAR_AND_BEARING_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAnalysisGearAndBearingRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_set_analysis(self) -> '_2635.CylindricalGearSetCompoundSystemDeflection':
        '''CylindricalGearSetCompoundSystemDeflection: 'GearSetAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2635.CylindricalGearSetCompoundSystemDeflection.TYPE not in self.wrapped.GearSetAnalysis.__class__.__mro__:
            raise CastException('Failed to cast gear_set_analysis to CylindricalGearSetCompoundSystemDeflection. Expected: {}.'.format(self.wrapped.GearSetAnalysis.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetAnalysis.__class__)(self.wrapped.GearSetAnalysis) if self.wrapped.GearSetAnalysis is not None else None

    @property
    def bearing_analyses(self) -> 'List[_2594.BearingCompoundSystemDeflection]':
        '''List[BearingCompoundSystemDeflection]: 'BearingAnalyses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BearingAnalyses, constructor.new(_2594.BearingCompoundSystemDeflection))
        return value
