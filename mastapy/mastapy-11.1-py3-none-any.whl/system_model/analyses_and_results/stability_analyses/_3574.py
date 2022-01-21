'''_3574.py

MassDiscStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6638
from mastapy.system_model.analyses_and_results.stability_analyses import _3623
from mastapy._internal.python_net import python_net_import

_MASS_DISC_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'MassDiscStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscStabilityAnalysis',)


class MassDiscStabilityAnalysis(_3623.VirtualComponentStabilityAnalysis):
    '''MassDiscStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6638.MassDiscLoadCase':
        '''MassDiscLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6638.MassDiscLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[MassDiscStabilityAnalysis]':
        '''List[MassDiscStabilityAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscStabilityAnalysis))
        return value
