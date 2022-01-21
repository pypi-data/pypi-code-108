'''_624.py

CutterHeadSlideError
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CUTTER_HEAD_SLIDE_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'CutterHeadSlideError')


__docformat__ = 'restructuredtext en'
__all__ = ('CutterHeadSlideError',)


class CutterHeadSlideError(_0.APIBase):
    '''CutterHeadSlideError

    This is a mastapy class.
    '''

    TYPE = _CUTTER_HEAD_SLIDE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CutterHeadSlideError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x_plane_measurement_length(self) -> 'float':
        '''float: 'XPlaneMeasurementLength' is the original name of this property.'''

        return self.wrapped.XPlaneMeasurementLength

    @x_plane_measurement_length.setter
    def x_plane_measurement_length(self, value: 'float'):
        self.wrapped.XPlaneMeasurementLength = float(value) if value else 0.0

    @property
    def y_plane_measurement_length(self) -> 'float':
        '''float: 'YPlaneMeasurementLength' is the original name of this property.'''

        return self.wrapped.YPlaneMeasurementLength

    @y_plane_measurement_length.setter
    def y_plane_measurement_length(self, value: 'float'):
        self.wrapped.YPlaneMeasurementLength = float(value) if value else 0.0

    @property
    def x_plane_measurement_reading(self) -> 'float':
        '''float: 'XPlaneMeasurementReading' is the original name of this property.'''

        return self.wrapped.XPlaneMeasurementReading

    @x_plane_measurement_reading.setter
    def x_plane_measurement_reading(self, value: 'float'):
        self.wrapped.XPlaneMeasurementReading = float(value) if value else 0.0

    @property
    def y_plane_measurement_reading(self) -> 'float':
        '''float: 'YPlaneMeasurementReading' is the original name of this property.'''

        return self.wrapped.YPlaneMeasurementReading

    @y_plane_measurement_reading.setter
    def y_plane_measurement_reading(self, value: 'float'):
        self.wrapped.YPlaneMeasurementReading = float(value) if value else 0.0

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
