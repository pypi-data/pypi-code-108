'''_3555.py

FEPartStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2194
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6602
from mastapy.system_model.analyses_and_results.stability_analyses import _3499
from mastapy._internal.python_net import python_net_import

_FE_PART_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'FEPartStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartStabilityAnalysis',)


class FEPartStabilityAnalysis(_3499.AbstractShaftOrHousingStabilityAnalysis):
    '''FEPartStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _FE_PART_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6602.FEPartLoadCase':
        '''FEPartLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6602.FEPartLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[FEPartStabilityAnalysis]':
        '''List[FEPartStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartStabilityAnalysis))
        return value
