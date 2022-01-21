'''_3602.py

SpringDamperHalfStabilityAnalysis
'''


from mastapy.system_model.part_model.couplings import _2341
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6676
from mastapy.system_model.analyses_and_results.stability_analyses import _3536
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'SpringDamperHalfStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalfStabilityAnalysis',)


class SpringDamperHalfStabilityAnalysis(_3536.CouplingHalfStabilityAnalysis):
    '''SpringDamperHalfStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalfStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2341.SpringDamperHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6676.SpringDamperHalfLoadCase':
        '''SpringDamperHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6676.SpringDamperHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
