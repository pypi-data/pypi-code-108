'''_3563.py

HypoidGearStabilityAnalysis
'''


from mastapy.system_model.part_model.gears import _2274
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6622
from mastapy.system_model.analyses_and_results.stability_analyses import _3504
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'HypoidGearStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearStabilityAnalysis',)


class HypoidGearStabilityAnalysis(_3504.AGMAGleasonConicalGearStabilityAnalysis):
    '''HypoidGearStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2274.HypoidGear':
        '''HypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2274.HypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6622.HypoidGearLoadCase':
        '''HypoidGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6622.HypoidGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
