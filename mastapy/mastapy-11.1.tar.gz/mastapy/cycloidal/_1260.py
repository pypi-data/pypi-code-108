'''_1260.py

RingPinsDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RING_PINS_DESIGN = python_net_import('SMT.MastaAPI.Cycloidal', 'RingPinsDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsDesign',)


class RingPinsDesign(_0.APIBase):
    '''RingPinsDesign

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length_of_pins(self) -> 'float':
        '''float: 'LengthOfPins' is the original name of this property.'''

        return self.wrapped.LengthOfPins

    @length_of_pins.setter
    def length_of_pins(self, value: 'float'):
        self.wrapped.LengthOfPins = float(value) if value else 0.0

    @property
    def pin_centre_circle_diameter(self) -> 'float':
        '''float: 'PinCentreCircleDiameter' is the original name of this property.'''

        return self.wrapped.PinCentreCircleDiameter

    @pin_centre_circle_diameter.setter
    def pin_centre_circle_diameter(self, value: 'float'):
        self.wrapped.PinCentreCircleDiameter = float(value) if value else 0.0

    @property
    def pin_diameter(self) -> 'float':
        '''float: 'PinDiameter' is the original name of this property.'''

        return self.wrapped.PinDiameter

    @pin_diameter.setter
    def pin_diameter(self, value: 'float'):
        self.wrapped.PinDiameter = float(value) if value else 0.0

    @property
    def number_of_pins(self) -> 'int':
        '''int: 'NumberOfPins' is the original name of this property.'''

        return self.wrapped.NumberOfPins

    @number_of_pins.setter
    def number_of_pins(self, value: 'int'):
        self.wrapped.NumberOfPins = int(value) if value else 0

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

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
