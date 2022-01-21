'''_6570.py

CVTPulleyLoadCase
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.couplings import _2327
from mastapy.system_model.analyses_and_results.static_loads import _6658
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'CVTPulleyLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyLoadCase',)


class CVTPulleyLoadCase(_6658.PulleyLoadCase):
    '''CVTPulleyLoadCase

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def effective_diameter(self) -> 'float':
        '''float: 'EffectiveDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveDiameter

    @property
    def clamping_force(self) -> 'float':
        '''float: 'ClampingForce' is the original name of this property.'''

        return self.wrapped.ClampingForce

    @clamping_force.setter
    def clamping_force(self, value: 'float'):
        self.wrapped.ClampingForce = float(value) if value else 0.0

    @property
    def number_of_nodes(self) -> 'int':
        '''int: 'NumberOfNodes' is the original name of this property.'''

        return self.wrapped.NumberOfNodes

    @number_of_nodes.setter
    def number_of_nodes(self, value: 'int'):
        self.wrapped.NumberOfNodes = int(value) if value else 0

    @property
    def component_design(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2327.CVTPulley)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
