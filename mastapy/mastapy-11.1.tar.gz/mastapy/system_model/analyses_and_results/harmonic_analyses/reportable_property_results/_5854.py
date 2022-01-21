'''_5854.py

SingleWhineAnalysisResultsPropertyAccessor
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5847, _5830
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'SingleWhineAnalysisResultsPropertyAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('SingleWhineAnalysisResultsPropertyAccessor',)


class SingleWhineAnalysisResultsPropertyAccessor(_5830.AbstractSingleWhineAnalysisResultsPropertyAccessor):
    '''SingleWhineAnalysisResultsPropertyAccessor

    This is a mastapy class.
    '''

    TYPE = _SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingleWhineAnalysisResultsPropertyAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def orders(self) -> 'List[_5847.ResultsForOrderIncludingNodes]':
        '''List[ResultsForOrderIncludingNodes]: 'Orders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Orders, constructor.new(_5847.ResultsForOrderIncludingNodes))
        return value
