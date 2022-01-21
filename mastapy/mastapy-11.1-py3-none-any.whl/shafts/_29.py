'''_29.py

ShaftProfile
'''


from typing import List

from mastapy.shafts import _30
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_PROFILE = python_net_import('SMT.MastaAPI.Shafts', 'ShaftProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftProfile',)


class ShaftProfile(_0.APIBase):
    '''ShaftProfile

    This is a mastapy class.
    '''

    TYPE = _SHAFT_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def points(self) -> 'List[_30.ShaftProfilePoint]':
        '''List[ShaftProfilePoint]: 'Points' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Points, constructor.new(_30.ShaftProfilePoint))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def add(self):
        ''' 'Add' is the original name of this method.'''

        self.wrapped.Add()

    def import_from_clipboard(self):
        ''' 'ImportFromClipboard' is the original name of this method.'''

        self.wrapped.ImportFromClipboard()

    def add_for_context_menu(self):
        ''' 'AddForContextMenu' is the original name of this method.'''

        self.wrapped.AddForContextMenu()

    def make_valid(self):
        ''' 'MakeValid' is the original name of this method.'''

        self.wrapped.MakeValid()

    def add_profile_point(self, offset: 'float', diameter: 'float'):
        ''' 'AddProfilePoint' is the original name of this method.

        Args:
            offset (float)
            diameter (float)
        '''

        offset = float(offset)
        diameter = float(diameter)
        self.wrapped.AddProfilePoint(offset if offset else 0.0, diameter if diameter else 0.0)

    def clear(self):
        ''' 'Clear' is the original name of this method.'''

        self.wrapped.Clear()

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
