'''_5830.py

AbstractSingleWhineAnalysisResultsPropertyAccessor
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'AbstractSingleWhineAnalysisResultsPropertyAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractSingleWhineAnalysisResultsPropertyAccessor',)


class AbstractSingleWhineAnalysisResultsPropertyAccessor(_0.APIBase):
    '''AbstractSingleWhineAnalysisResultsPropertyAccessor

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractSingleWhineAnalysisResultsPropertyAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
