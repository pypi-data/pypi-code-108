'''_756.py

FlankMeasurementBorder
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FLANK_MEASUREMENT_BORDER = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'FlankMeasurementBorder')


__docformat__ = 'restructuredtext en'
__all__ = ('FlankMeasurementBorder',)


class FlankMeasurementBorder(_0.APIBase):
    '''FlankMeasurementBorder

    This is a mastapy class.
    '''

    TYPE = _FLANK_MEASUREMENT_BORDER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlankMeasurementBorder.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def percent_of_face_width_at_heel(self) -> 'float':
        '''float: 'PercentOfFaceWidthAtHeel' is the original name of this property.'''

        return self.wrapped.PercentOfFaceWidthAtHeel

    @percent_of_face_width_at_heel.setter
    def percent_of_face_width_at_heel(self, value: 'float'):
        self.wrapped.PercentOfFaceWidthAtHeel = float(value) if value else 0.0

    @property
    def percent_of_face_width_at_toe(self) -> 'float':
        '''float: 'PercentOfFaceWidthAtToe' is the original name of this property.'''

        return self.wrapped.PercentOfFaceWidthAtToe

    @percent_of_face_width_at_toe.setter
    def percent_of_face_width_at_toe(self, value: 'float'):
        self.wrapped.PercentOfFaceWidthAtToe = float(value) if value else 0.0

    @property
    def percent_of_working_depth_at_tip(self) -> 'float':
        '''float: 'PercentOfWorkingDepthAtTip' is the original name of this property.'''

        return self.wrapped.PercentOfWorkingDepthAtTip

    @percent_of_working_depth_at_tip.setter
    def percent_of_working_depth_at_tip(self, value: 'float'):
        self.wrapped.PercentOfWorkingDepthAtTip = float(value) if value else 0.0

    @property
    def percent_of_working_depth_at_root(self) -> 'float':
        '''float: 'PercentOfWorkingDepthAtRoot' is the original name of this property.'''

        return self.wrapped.PercentOfWorkingDepthAtRoot

    @percent_of_working_depth_at_root.setter
    def percent_of_working_depth_at_root(self, value: 'float'):
        self.wrapped.PercentOfWorkingDepthAtRoot = float(value) if value else 0.0

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
