'''_987.py

CylindricalGearSetManufacturingConfigurationSelection
'''


from typing import List

from mastapy._internal.implicit import list_with_selected_item
from mastapy.gears.manufacturing.cylindrical import _585
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_MANUFACTURING_CONFIGURATION_SELECTION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearSetManufacturingConfigurationSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetManufacturingConfigurationSelection',)


class CylindricalGearSetManufacturingConfigurationSelection(_0.APIBase):
    '''CylindricalGearSetManufacturingConfigurationSelection

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_MANUFACTURING_CONFIGURATION_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetManufacturingConfigurationSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def manufacturing_configuration(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalSetManufacturingConfig':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalSetManufacturingConfig: 'ManufacturingConfiguration' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalSetManufacturingConfig)(self.wrapped.ManufacturingConfiguration) if self.wrapped.ManufacturingConfiguration is not None else None

    @manufacturing_configuration.setter
    def manufacturing_configuration(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalSetManufacturingConfig.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalSetManufacturingConfig.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalSetManufacturingConfig.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.ManufacturingConfiguration = value

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
