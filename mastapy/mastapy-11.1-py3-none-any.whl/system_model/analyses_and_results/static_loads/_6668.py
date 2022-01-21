'''_6668.py

ShaftLoadCase
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.analyses_and_results.static_loads import _6522
from mastapy._internal.python_net import python_net_import

_SHAFT_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ShaftLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftLoadCase',)


class ShaftLoadCase(_6522.AbstractShaftLoadCase):
    '''ShaftLoadCase

    This is a mastapy class.
    '''

    TYPE = _SHAFT_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diameter_scaling_factor(self) -> 'float':
        '''float: 'DiameterScalingFactor' is the original name of this property.'''

        return self.wrapped.DiameterScalingFactor

    @diameter_scaling_factor.setter
    def diameter_scaling_factor(self, value: 'float'):
        self.wrapped.DiameterScalingFactor = float(value) if value else 0.0

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def planetaries(self) -> 'List[ShaftLoadCase]':
        '''List[ShaftLoadCase]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftLoadCase))
        return value
