'''_5853.py

RootAssemblySingleWhineAnalysisResultsPropertyAccessor
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5846, _5830
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'RootAssemblySingleWhineAnalysisResultsPropertyAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblySingleWhineAnalysisResultsPropertyAccessor',)


class RootAssemblySingleWhineAnalysisResultsPropertyAccessor(_5830.AbstractSingleWhineAnalysisResultsPropertyAccessor):
    '''RootAssemblySingleWhineAnalysisResultsPropertyAccessor

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_SINGLE_WHINE_ANALYSIS_RESULTS_PROPERTY_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblySingleWhineAnalysisResultsPropertyAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def orders(self) -> 'List[_5846.ResultsForOrderIncludingGroups]':
        '''List[ResultsForOrderIncludingGroups]: 'Orders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Orders, constructor.new(_5846.ResultsForOrderIncludingGroups))
        return value
