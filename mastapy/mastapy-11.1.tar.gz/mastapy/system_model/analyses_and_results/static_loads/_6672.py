'''_6672.py

SpiralBevelGearLoadCase
'''


from mastapy.system_model.part_model.gears import _2283
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6542
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'SpiralBevelGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearLoadCase',)


class SpiralBevelGearLoadCase(_6542.BevelGearLoadCase):
    '''SpiralBevelGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2283.SpiralBevelGear':
        '''SpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2283.SpiralBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
