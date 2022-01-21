'''_5734.py

FrequencyOptionsForHarmonicAnalysisResults
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7253
from mastapy.system_model.analyses_and_results.static_loads import _6519
from mastapy._internal.python_net import python_net_import

_FREQUENCY_OPTIONS_FOR_HARMONIC_ANALYSIS_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'FrequencyOptionsForHarmonicAnalysisResults')


__docformat__ = 'restructuredtext en'
__all__ = ('FrequencyOptionsForHarmonicAnalysisResults',)


class FrequencyOptionsForHarmonicAnalysisResults(_7253.AbstractAnalysisOptions['_6519.StaticLoadCase']):
    '''FrequencyOptionsForHarmonicAnalysisResults

    This is a mastapy class.
    '''

    TYPE = _FREQUENCY_OPTIONS_FOR_HARMONIC_ANALYSIS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FrequencyOptionsForHarmonicAnalysisResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Minimum' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Minimum) if self.wrapped.Minimum is not None else None

    @minimum.setter
    def minimum(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Minimum = value

    @property
    def maximum(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Maximum' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Maximum) if self.wrapped.Maximum is not None else None

    @maximum.setter
    def maximum(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Maximum = value

    @property
    def create_data_points_at_mode_frequencies(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'CreateDataPointsAtModeFrequencies' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.CreateDataPointsAtModeFrequencies) if self.wrapped.CreateDataPointsAtModeFrequencies is not None else None

    @create_data_points_at_mode_frequencies.setter
    def create_data_points_at_mode_frequencies(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.CreateDataPointsAtModeFrequencies = value

    @property
    def additional_data_points_per_harmonic(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'AdditionalDataPointsPerHarmonic' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.AdditionalDataPointsPerHarmonic) if self.wrapped.AdditionalDataPointsPerHarmonic is not None else None

    @additional_data_points_per_harmonic.setter
    def additional_data_points_per_harmonic(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.AdditionalDataPointsPerHarmonic = value

    @property
    def clustering_bias_of_additional_data_points(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ClusteringBiasOfAdditionalDataPoints' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ClusteringBiasOfAdditionalDataPoints) if self.wrapped.ClusteringBiasOfAdditionalDataPoints is not None else None

    @clustering_bias_of_additional_data_points.setter
    def clustering_bias_of_additional_data_points(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ClusteringBiasOfAdditionalDataPoints = value

    @property
    def total_number_of_data_points_per_harmonic(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'TotalNumberOfDataPointsPerHarmonic' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.TotalNumberOfDataPointsPerHarmonic) if self.wrapped.TotalNumberOfDataPointsPerHarmonic is not None else None

    @total_number_of_data_points_per_harmonic.setter
    def total_number_of_data_points_per_harmonic(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.TotalNumberOfDataPointsPerHarmonic = value

    @property
    def logarithmic_frequency_axis(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'LogarithmicFrequencyAxis' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.LogarithmicFrequencyAxis) if self.wrapped.LogarithmicFrequencyAxis is not None else None

    @logarithmic_frequency_axis.setter
    def logarithmic_frequency_axis(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.LogarithmicFrequencyAxis = value

    @property
    def use_logarithmic_spacing_for_frequency_values(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'UseLogarithmicSpacingForFrequencyValues' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.UseLogarithmicSpacingForFrequencyValues) if self.wrapped.UseLogarithmicSpacingForFrequencyValues is not None else None

    @use_logarithmic_spacing_for_frequency_values.setter
    def use_logarithmic_spacing_for_frequency_values(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.UseLogarithmicSpacingForFrequencyValues = value

    @property
    def design_defaults(self) -> 'FrequencyOptionsForHarmonicAnalysisResults':
        '''FrequencyOptionsForHarmonicAnalysisResults: 'DesignDefaults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(FrequencyOptionsForHarmonicAnalysisResults)(self.wrapped.DesignDefaults) if self.wrapped.DesignDefaults is not None else None

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
