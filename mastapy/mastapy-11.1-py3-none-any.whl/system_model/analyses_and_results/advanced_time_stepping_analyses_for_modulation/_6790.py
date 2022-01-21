'''_6790.py

HarmonicAnalysisOptionsForAdvancedTimeSteppingAnalysisForModulation
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5746
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_OPTIONS_FOR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'HarmonicAnalysisOptionsForAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisOptionsForAdvancedTimeSteppingAnalysisForModulation',)


class HarmonicAnalysisOptionsForAdvancedTimeSteppingAnalysisForModulation(_5746.HarmonicAnalysisOptions):
    '''HarmonicAnalysisOptionsForAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ANALYSIS_OPTIONS_FOR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisOptionsForAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def crop_to_speed_range_for_export_and_reports(self) -> 'bool':
        '''bool: 'CropToSpeedRangeForExportAndReports' is the original name of this property.'''

        return self.wrapped.CropToSpeedRangeForExportAndReports

    @crop_to_speed_range_for_export_and_reports.setter
    def crop_to_speed_range_for_export_and_reports(self, value: 'bool'):
        self.wrapped.CropToSpeedRangeForExportAndReports = bool(value) if value else False

    @property
    def calculate_uncoupled_modes_during_analysis(self) -> 'bool':
        '''bool: 'CalculateUncoupledModesDuringAnalysis' is the original name of this property.'''

        return self.wrapped.CalculateUncoupledModesDuringAnalysis

    @calculate_uncoupled_modes_during_analysis.setter
    def calculate_uncoupled_modes_during_analysis(self, value: 'bool'):
        self.wrapped.CalculateUncoupledModesDuringAnalysis = bool(value) if value else False
