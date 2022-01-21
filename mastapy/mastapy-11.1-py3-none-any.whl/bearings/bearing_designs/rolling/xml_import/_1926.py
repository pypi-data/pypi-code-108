'''_1926.py

XmlBearingTypeMapping
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.bearings.bearing_designs.rolling.xml_import import _1924, _1923
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_XML_BEARING_TYPE_MAPPING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling.XmlImport', 'XmlBearingTypeMapping')


__docformat__ = 'restructuredtext en'
__all__ = ('XmlBearingTypeMapping',)


class XmlBearingTypeMapping(_0.APIBase):
    '''XmlBearingTypeMapping

    This is a mastapy class.
    '''

    TYPE = _XML_BEARING_TYPE_MAPPING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'XmlBearingTypeMapping.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def source_name(self) -> 'str':
        '''str: 'SourceName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SourceName

    @property
    def target_type(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'TargetType' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.TargetType) if self.wrapped.TargetType is not None else None

    @target_type.setter
    def target_type(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.TargetType = value

    @property
    def number_of_bearings(self) -> 'int':
        '''int: 'NumberOfBearings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfBearings

    @property
    def number_of_variables(self) -> 'int':
        '''int: 'NumberOfVariables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfVariables

    @property
    def number_of_unassigned_variables(self) -> 'int':
        '''int: 'NumberOfUnassignedVariables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfUnassignedVariables

    @property
    def files(self) -> 'List[_1924.BearingImportFile]':
        '''List[BearingImportFile]: 'Files' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Files, constructor.new(_1924.BearingImportFile))
        return value

    @property
    def variables(self) -> 'List[_1923.AbstractXmlVariableAssignment]':
        '''List[AbstractXmlVariableAssignment]: 'Variables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Variables, constructor.new(_1923.AbstractXmlVariableAssignment))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def import_all(self):
        ''' 'ImportAll' is the original name of this method.'''

        self.wrapped.ImportAll()

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
