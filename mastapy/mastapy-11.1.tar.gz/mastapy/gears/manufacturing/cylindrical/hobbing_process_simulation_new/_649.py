'''_649.py

RackManufactureError
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RACK_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'RackManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('RackManufactureError',)


class RackManufactureError(_0.APIBase):
    '''RackManufactureError

    This is a mastapy class.
    '''

    TYPE = _RACK_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RackManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def left_flank_pressure_angle_error_length(self) -> 'float':
        '''float: 'LeftFlankPressureAngleErrorLength' is the original name of this property.'''

        return self.wrapped.LeftFlankPressureAngleErrorLength

    @left_flank_pressure_angle_error_length.setter
    def left_flank_pressure_angle_error_length(self, value: 'float'):
        self.wrapped.LeftFlankPressureAngleErrorLength = float(value) if value else 0.0

    @property
    def right_flank_pressure_angle_error_length(self) -> 'float':
        '''float: 'RightFlankPressureAngleErrorLength' is the original name of this property.'''

        return self.wrapped.RightFlankPressureAngleErrorLength

    @right_flank_pressure_angle_error_length.setter
    def right_flank_pressure_angle_error_length(self, value: 'float'):
        self.wrapped.RightFlankPressureAngleErrorLength = float(value) if value else 0.0

    @property
    def left_flank_pressure_angle_error_reading(self) -> 'float':
        '''float: 'LeftFlankPressureAngleErrorReading' is the original name of this property.'''

        return self.wrapped.LeftFlankPressureAngleErrorReading

    @left_flank_pressure_angle_error_reading.setter
    def left_flank_pressure_angle_error_reading(self, value: 'float'):
        self.wrapped.LeftFlankPressureAngleErrorReading = float(value) if value else 0.0

    @property
    def right_flank_pressure_angle_error_reading(self) -> 'float':
        '''float: 'RightFlankPressureAngleErrorReading' is the original name of this property.'''

        return self.wrapped.RightFlankPressureAngleErrorReading

    @right_flank_pressure_angle_error_reading.setter
    def right_flank_pressure_angle_error_reading(self, value: 'float'):
        self.wrapped.RightFlankPressureAngleErrorReading = float(value) if value else 0.0

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
