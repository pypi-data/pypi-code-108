'''_5847.py

ResultsForOrderIncludingNodes
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5839, _5845
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_RESULTS_FOR_ORDER_INCLUDING_NODES = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'ResultsForOrderIncludingNodes')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultsForOrderIncludingNodes',)


class ResultsForOrderIncludingNodes(_5845.ResultsForOrder):
    '''ResultsForOrderIncludingNodes

    This is a mastapy class.
    '''

    TYPE = _RESULTS_FOR_ORDER_INCLUDING_NODES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResultsForOrderIncludingNodes.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def node_results_global_coordinate_system(self) -> 'List[_5839.HarmonicAnalysisResultsBrokenDownByNodeWithinAHarmonic]':
        '''List[HarmonicAnalysisResultsBrokenDownByNodeWithinAHarmonic]: 'NodeResultsGlobalCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.NodeResultsGlobalCoordinateSystem, constructor.new(_5839.HarmonicAnalysisResultsBrokenDownByNodeWithinAHarmonic))
        return value

    @property
    def node_results_local_coordinate_system(self) -> 'List[_5839.HarmonicAnalysisResultsBrokenDownByNodeWithinAHarmonic]':
        '''List[HarmonicAnalysisResultsBrokenDownByNodeWithinAHarmonic]: 'NodeResultsLocalCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.NodeResultsLocalCoordinateSystem, constructor.new(_5839.HarmonicAnalysisResultsBrokenDownByNodeWithinAHarmonic))
        return value
