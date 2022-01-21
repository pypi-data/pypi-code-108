'''_3540.py

CVTPulleyStabilityAnalysis
'''


from mastapy.system_model.part_model.couplings import _2327
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.stability_analyses import _3587
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'CVTPulleyStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyStabilityAnalysis',)


class CVTPulleyStabilityAnalysis(_3587.PulleyStabilityAnalysis):
    '''CVTPulleyStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2327.CVTPulley)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
