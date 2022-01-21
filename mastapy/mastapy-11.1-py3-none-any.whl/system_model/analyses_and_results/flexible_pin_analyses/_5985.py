'''_5985.py

FlexiblePinAnalysis
'''


from mastapy.system_model.analyses_and_results.flexible_pin_analyses import _5990, _5984
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_PIN_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.FlexiblePinAnalyses', 'FlexiblePinAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAnalysis',)


class FlexiblePinAnalysis(_5984.CombinationAnalysis):
    '''FlexiblePinAnalysis

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def analysis_options(self) -> '_5990.FlexiblePinAnalysisOptions':
        '''FlexiblePinAnalysisOptions: 'AnalysisOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5990.FlexiblePinAnalysisOptions)(self.wrapped.AnalysisOptions) if self.wrapped.AnalysisOptions is not None else None
