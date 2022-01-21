'''_6676.py

SpringDamperHalfLoadCase
'''


from mastapy.system_model.part_model.couplings import _2341
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6566
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'SpringDamperHalfLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalfLoadCase',)


class SpringDamperHalfLoadCase(_6566.CouplingHalfLoadCase):
    '''SpringDamperHalfLoadCase

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalfLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2341.SpringDamperHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
