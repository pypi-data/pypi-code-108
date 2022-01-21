'''_5841.py

HarmonicAnalysisResultsPropertyAccessor
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5854, _5847
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_RESULTS_PROPERTY_ACCESSOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'HarmonicAnalysisResultsPropertyAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisResultsPropertyAccessor',)


class HarmonicAnalysisResultsPropertyAccessor(_0.APIBase):
    '''HarmonicAnalysisResultsPropertyAccessor

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_RESULTS_PROPERTY_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisResultsPropertyAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def excitations(self) -> 'List[_5854.SingleWhineAnalysisResultsPropertyAccessor]':
        '''List[SingleWhineAnalysisResultsPropertyAccessor]: 'Excitations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Excitations, constructor.new(_5854.SingleWhineAnalysisResultsPropertyAccessor))
        return value

    @property
    def orders_for_combined_excitations(self) -> 'List[_5847.ResultsForOrderIncludingNodes]':
        '''List[ResultsForOrderIncludingNodes]: 'OrdersForCombinedExcitations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OrdersForCombinedExcitations, constructor.new(_5847.ResultsForOrderIncludingNodes))
        return value

    @property
    def orders_for_combined_excitations_from_same_parts(self) -> 'List[_5847.ResultsForOrderIncludingNodes]':
        '''List[ResultsForOrderIncludingNodes]: 'OrdersForCombinedExcitationsFromSameParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OrdersForCombinedExcitationsFromSameParts, constructor.new(_5847.ResultsForOrderIncludingNodes))
        return value
