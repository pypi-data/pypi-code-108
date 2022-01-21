'''_5835.py

HarmonicAnalysisCombinedForMultipleSurfacesWithinAHarmonic
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5840
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_COMBINED_FOR_MULTIPLE_SURFACES_WITHIN_A_HARMONIC = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'HarmonicAnalysisCombinedForMultipleSurfacesWithinAHarmonic')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisCombinedForMultipleSurfacesWithinAHarmonic',)


class HarmonicAnalysisCombinedForMultipleSurfacesWithinAHarmonic(_5840.HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic):
    '''HarmonicAnalysisCombinedForMultipleSurfacesWithinAHarmonic

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_COMBINED_FOR_MULTIPLE_SURFACES_WITHIN_A_HARMONIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisCombinedForMultipleSurfacesWithinAHarmonic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def surface_names(self) -> 'str':
        '''str: 'SurfaceNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceNames
