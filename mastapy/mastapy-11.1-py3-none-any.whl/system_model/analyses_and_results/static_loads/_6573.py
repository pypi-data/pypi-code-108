'''_6573.py

CycloidalDiscLoadCase
'''


from mastapy.system_model.part_model.cycloidal import _2309
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6522
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'CycloidalDiscLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscLoadCase',)


class CycloidalDiscLoadCase(_6522.AbstractShaftLoadCase):
    '''CycloidalDiscLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2309.CycloidalDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
