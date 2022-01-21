'''_274.py

ClippingPlane
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.math_utility import _1290
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CLIPPING_PLANE = python_net_import('SMT.MastaAPI.Geometry', 'ClippingPlane')


__docformat__ = 'restructuredtext en'
__all__ = ('ClippingPlane',)


class ClippingPlane(_0.APIBase):
    '''ClippingPlane

    This is a mastapy class.
    '''

    TYPE = _CLIPPING_PLANE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClippingPlane.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_enabled(self) -> 'bool':
        '''bool: 'IsEnabled' is the original name of this property.'''

        return self.wrapped.IsEnabled

    @is_enabled.setter
    def is_enabled(self, value: 'bool'):
        self.wrapped.IsEnabled = bool(value) if value else False

    @property
    def axis(self) -> '_1290.Axis':
        '''Axis: 'Axis' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Axis)
        return constructor.new(_1290.Axis)(value) if value is not None else None

    @axis.setter
    def axis(self, value: '_1290.Axis'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Axis = value

    @property
    def is_flipped(self) -> 'bool':
        '''bool: 'IsFlipped' is the original name of this property.'''

        return self.wrapped.IsFlipped

    @is_flipped.setter
    def is_flipped(self, value: 'bool'):
        self.wrapped.IsFlipped = bool(value) if value else False

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
