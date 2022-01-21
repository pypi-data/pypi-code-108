'''_5846.py

ResultsForOrderIncludingGroups
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5837, _5845
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_RESULTS_FOR_ORDER_INCLUDING_GROUPS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'ResultsForOrderIncludingGroups')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultsForOrderIncludingGroups',)


class ResultsForOrderIncludingGroups(_5845.ResultsForOrder):
    '''ResultsForOrderIncludingGroups

    This is a mastapy class.
    '''

    TYPE = _RESULTS_FOR_ORDER_INCLUDING_GROUPS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResultsForOrderIncludingGroups.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def groups(self) -> 'List[_5837.HarmonicAnalysisResultsBrokenDownByGroupsWithinAHarmonic]':
        '''List[HarmonicAnalysisResultsBrokenDownByGroupsWithinAHarmonic]: 'Groups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Groups, constructor.new(_5837.HarmonicAnalysisResultsBrokenDownByGroupsWithinAHarmonic))
        return value
