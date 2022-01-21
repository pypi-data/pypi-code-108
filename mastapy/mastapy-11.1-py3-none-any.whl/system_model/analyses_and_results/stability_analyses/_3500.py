'''_3500.py

AbstractShaftStabilityAnalysis
'''


from mastapy.system_model.part_model import _2178
from mastapy._internal import constructor
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.cycloidal import _2309
from mastapy.system_model.analyses_and_results.stability_analyses import _3499
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'AbstractShaftStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftStabilityAnalysis',)


class AbstractShaftStabilityAnalysis(_3499.AbstractShaftOrHousingStabilityAnalysis):
    '''AbstractShaftStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to AbstractShaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Shaft. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CycloidalDisc. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
