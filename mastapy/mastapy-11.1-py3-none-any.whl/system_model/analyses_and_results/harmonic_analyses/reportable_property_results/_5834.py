'''_5834.py

FEPartSingleWhineAnalysisResultsPropertyAccessor
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5848, _5854
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_FE_PART_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'FEPartSingleWhineAnalysisResultsPropertyAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartSingleWhineAnalysisResultsPropertyAccessor',)


class FEPartSingleWhineAnalysisResultsPropertyAccessor(_5854.SingleWhineAnalysisResultsPropertyAccessor):
    '''FEPartSingleWhineAnalysisResultsPropertyAccessor

    This is a mastapy class.
    '''

    TYPE = _FE_PART_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartSingleWhineAnalysisResultsPropertyAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def orders(self) -> 'List[_5848.ResultsForOrderIncludingSurfaces]':
        '''List[ResultsForOrderIncludingSurfaces]: 'Orders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Orders, constructor.new(_5848.ResultsForOrderIncludingSurfaces))
        return value
