'''_5836.py

HarmonicAnalysisResultsBrokenDownByComponentWithinAHarmonic
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5849, _5838
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_RESULTS_BROKEN_DOWN_BY_COMPONENT_WITHIN_A_HARMONIC = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'HarmonicAnalysisResultsBrokenDownByComponentWithinAHarmonic')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisResultsBrokenDownByComponentWithinAHarmonic',)


class HarmonicAnalysisResultsBrokenDownByComponentWithinAHarmonic(_5838.HarmonicAnalysisResultsBrokenDownByLocationWithinAHarmonic):
    '''HarmonicAnalysisResultsBrokenDownByComponentWithinAHarmonic

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_RESULTS_BROKEN_DOWN_BY_COMPONENT_WITHIN_A_HARMONIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisResultsBrokenDownByComponentWithinAHarmonic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_name(self) -> 'str':
        '''str: 'ComponentName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComponentName

    @property
    def kinetic_energy(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'KineticEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.KineticEnergy) if self.wrapped.KineticEnergy is not None else None

    @property
    def strain_energy(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'StrainEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.StrainEnergy) if self.wrapped.StrainEnergy is not None else None

    @property
    def dynamic_mesh_force(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'DynamicMeshForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.DynamicMeshForce) if self.wrapped.DynamicMeshForce is not None else None

    @property
    def dynamic_mesh_moment(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'DynamicMeshMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.DynamicMeshMoment) if self.wrapped.DynamicMeshMoment is not None else None

    @property
    def dynamic_te(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'DynamicTE' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.DynamicTE) if self.wrapped.DynamicTE is not None else None

    @property
    def dynamic_misalignment(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'DynamicMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.DynamicMisalignment) if self.wrapped.DynamicMisalignment is not None else None
