'''_6658.py

PulleyLoadCase
'''


from mastapy.system_model.part_model.couplings import _2330, _2327
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6566
from mastapy._internal.python_net import python_net_import

_PULLEY_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PulleyLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PulleyLoadCase',)


class PulleyLoadCase(_6566.CouplingHalfLoadCase):
    '''PulleyLoadCase

    This is a mastapy class.
    '''

    TYPE = _PULLEY_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PulleyLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2330.Pulley':
        '''Pulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2330.Pulley.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Pulley. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
