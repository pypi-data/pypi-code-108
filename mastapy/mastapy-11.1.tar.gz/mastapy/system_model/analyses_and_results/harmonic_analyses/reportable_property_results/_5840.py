'''_5840.py

HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses.reportable_property_results import _5849, _5838
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_RESULTS_BROKEN_DOWN_BY_SURFACE_WITHIN_A_HARMONIC = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic',)


class HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic(_5838.HarmonicAnalysisResultsBrokenDownByLocationWithinAHarmonic):
    '''HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_RESULTS_BROKEN_DOWN_BY_SURFACE_WITHIN_A_HARMONIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisResultsBrokenDownBySurfaceWithinAHarmonic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def surface_name(self) -> 'str':
        '''str: 'SurfaceName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceName

    @property
    def root_mean_squared_normal_displacement(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'RootMeanSquaredNormalDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.RootMeanSquaredNormalDisplacement) if self.wrapped.RootMeanSquaredNormalDisplacement is not None else None

    @property
    def root_mean_squared_normal_velocity(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'RootMeanSquaredNormalVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.RootMeanSquaredNormalVelocity) if self.wrapped.RootMeanSquaredNormalVelocity is not None else None

    @property
    def maximum_normal_velocity(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'MaximumNormalVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.MaximumNormalVelocity) if self.wrapped.MaximumNormalVelocity is not None else None

    @property
    def root_mean_squared_normal_acceleration(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'RootMeanSquaredNormalAcceleration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.RootMeanSquaredNormalAcceleration) if self.wrapped.RootMeanSquaredNormalAcceleration is not None else None

    @property
    def airborne_sound_power(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'AirborneSoundPower' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.AirborneSoundPower) if self.wrapped.AirborneSoundPower is not None else None

    @property
    def sound_intensity(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'SoundIntensity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.SoundIntensity) if self.wrapped.SoundIntensity is not None else None

    @property
    def sound_pressure(self) -> '_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic':
        '''ResultsForResponseOfAComponentOrSurfaceInAHarmonic: 'SoundPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5849.ResultsForResponseOfAComponentOrSurfaceInAHarmonic)(self.wrapped.SoundPressure) if self.wrapped.SoundPressure is not None else None
