'''_3600.py

SpiralBevelGearStabilityAnalysis
'''


from mastapy.system_model.part_model.gears import _2283
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6672
from mastapy.system_model.analyses_and_results.stability_analyses import _3516
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'SpiralBevelGearStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearStabilityAnalysis',)


class SpiralBevelGearStabilityAnalysis(_3516.BevelGearStabilityAnalysis):
    '''SpiralBevelGearStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2283.SpiralBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6672.SpiralBevelGearLoadCase':
        '''SpiralBevelGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6672.SpiralBevelGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
