'''_5848.py

ResultsForOrderIncludingSurfaces
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5840, _5847
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_RESULTS_FOR_ORDER_INCLUDING_SURFACES = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'ResultsForOrderIncludingSurfaces')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultsForOrderIncludingSurfaces',)


class ResultsForOrderIncludingSurfaces(_5847.ResultsForOrderIncludingNodes):
    '''ResultsForOrderIncludingSurfaces

    This is a mastapy class.
    '''

    TYPE = _RESULTS_FOR_ORDER_INCLUDING_SURFACES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResultsForOrderIncludingSurfaces.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def fe_surfaces(self) -> 'List[_5840.HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic]':
        '''List[HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic]: 'FESurfaces' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FESurfaces, constructor.new(_5840.HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic))
        return value
