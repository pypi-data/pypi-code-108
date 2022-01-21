'''_6701.py

WormGearLoadCase
'''


from mastapy.system_model.part_model.gears import _2291
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6605
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'WormGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearLoadCase',)


class WormGearLoadCase(_6605.GearLoadCase):
    '''WormGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2291.WormGear':
        '''WormGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2291.WormGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
