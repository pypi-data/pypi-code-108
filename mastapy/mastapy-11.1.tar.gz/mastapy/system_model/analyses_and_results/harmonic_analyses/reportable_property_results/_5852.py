'''_5852.py

RootAssemblyHarmonicAnalysisResultsPropertyAccessor
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5844, _5853, _5846
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_HARMONIC_ANALYSIS_RESULTS_PROPERTY_ACCESSOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'RootAssemblyHarmonicAnalysisResultsPropertyAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyHarmonicAnalysisResultsPropertyAccessor',)


class RootAssemblyHarmonicAnalysisResultsPropertyAccessor(_0.APIBase):
    '''RootAssemblyHarmonicAnalysisResultsPropertyAccessor

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_HARMONIC_ANALYSIS_RESULTS_PROPERTY_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyHarmonicAnalysisResultsPropertyAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def combined_orders(self) -> '_5844.ResultsForMultipleOrdersForGroups':
        '''ResultsForMultipleOrdersForGroups: 'CombinedOrders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5844.ResultsForMultipleOrdersForGroups)(self.wrapped.CombinedOrders) if self.wrapped.CombinedOrders is not None else None

    @property
    def excitations(self) -> 'List[_5853.RootAssemblySingleWhineAnalysisResultsPropertyAccessor]':
        '''List[RootAssemblySingleWhineAnalysisResultsPropertyAccessor]: 'Excitations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Excitations, constructor.new(_5853.RootAssemblySingleWhineAnalysisResultsPropertyAccessor))
        return value

    @property
    def orders_for_combined_excitations(self) -> 'List[_5846.ResultsForOrderIncludingGroups]':
        '''List[ResultsForOrderIncludingGroups]: 'OrdersForCombinedExcitations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OrdersForCombinedExcitations, constructor.new(_5846.ResultsForOrderIncludingGroups))
        return value

    @property
    def orders_for_combined_excitations_from_same_parts(self) -> 'List[_5846.ResultsForOrderIncludingGroups]':
        '''List[ResultsForOrderIncludingGroups]: 'OrdersForCombinedExcitationsFromSameParts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OrdersForCombinedExcitationsFromSameParts, constructor.new(_5846.ResultsForOrderIncludingGroups))
        return value
