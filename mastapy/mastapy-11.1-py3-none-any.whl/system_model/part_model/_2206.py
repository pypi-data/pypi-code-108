'''_2206.py

OilLevelSpecification
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.part_model import _2190
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.part_model.gears import _2265
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OIL_LEVEL_SPECIFICATION = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'OilLevelSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('OilLevelSpecification',)


class OilLevelSpecification(_0.APIBase):
    '''OilLevelSpecification

    This is a mastapy class.
    '''

    TYPE = _OIL_LEVEL_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilLevelSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def oil_level_specified(self) -> 'bool':
        '''bool: 'OilLevelSpecified' is the original name of this property.'''

        return self.wrapped.OilLevelSpecified

    @oil_level_specified.setter
    def oil_level_specified(self, value: 'bool'):
        self.wrapped.OilLevelSpecified = bool(value) if value else False

    @property
    def oil_level_reference_datum(self) -> 'list_with_selected_item.ListWithSelectedItem_Datum':
        '''list_with_selected_item.ListWithSelectedItem_Datum: 'OilLevelReferenceDatum' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Datum)(self.wrapped.OilLevelReferenceDatum) if self.wrapped.OilLevelReferenceDatum is not None else None

    @oil_level_reference_datum.setter
    def oil_level_reference_datum(self, value: 'list_with_selected_item.ListWithSelectedItem_Datum.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Datum.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Datum.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.OilLevelReferenceDatum = value

    @property
    def use_gear_tip_diameter_for_oil_level_reference(self) -> 'bool':
        '''bool: 'UseGearTipDiameterForOilLevelReference' is the original name of this property.'''

        return self.wrapped.UseGearTipDiameterForOilLevelReference

    @use_gear_tip_diameter_for_oil_level_reference.setter
    def use_gear_tip_diameter_for_oil_level_reference(self, value: 'bool'):
        self.wrapped.UseGearTipDiameterForOilLevelReference = bool(value) if value else False

    @property
    def gear_for_oil_level_reference(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalGear':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalGear: 'GearForOilLevelReference' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalGear)(self.wrapped.GearForOilLevelReference) if self.wrapped.GearForOilLevelReference is not None else None

    @gear_for_oil_level_reference.setter
    def gear_for_oil_level_reference(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalGear.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalGear.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalGear.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.GearForOilLevelReference = value

    @property
    def oil_level(self) -> 'float':
        '''float: 'OilLevel' is the original name of this property.'''

        return self.wrapped.OilLevel

    @oil_level.setter
    def oil_level(self, value: 'float'):
        self.wrapped.OilLevel = float(value) if value else 0.0

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
