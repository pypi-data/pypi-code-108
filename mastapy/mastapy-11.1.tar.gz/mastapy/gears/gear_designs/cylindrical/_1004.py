'''_1004.py

GearSetManufacturingConfigurationSetup
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.cylindrical import _959, _1003
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_SET_MANUFACTURING_CONFIGURATION_SETUP = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'GearSetManufacturingConfigurationSetup')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetManufacturingConfigurationSetup',)


class GearSetManufacturingConfigurationSetup(_0.APIBase):
    '''GearSetManufacturingConfigurationSetup

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_MANUFACTURING_CONFIGURATION_SETUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetManufacturingConfigurationSetup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def create_new_suitable_cutters(self) -> '_959.CreateNewSuitableCutterOption':
        '''CreateNewSuitableCutterOption: 'CreateNewSuitableCutters' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CreateNewSuitableCutters)
        return constructor.new(_959.CreateNewSuitableCutterOption)(value) if value is not None else None

    @create_new_suitable_cutters.setter
    def create_new_suitable_cutters(self, value: '_959.CreateNewSuitableCutterOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CreateNewSuitableCutters = value

    @property
    def use_as_design_mode_geometry(self) -> '_959.CreateNewSuitableCutterOption':
        '''CreateNewSuitableCutterOption: 'UseAsDesignModeGeometry' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.UseAsDesignModeGeometry)
        return constructor.new(_959.CreateNewSuitableCutterOption)(value) if value is not None else None

    @use_as_design_mode_geometry.setter
    def use_as_design_mode_geometry(self, value: '_959.CreateNewSuitableCutterOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.UseAsDesignModeGeometry = value

    @property
    def gears(self) -> 'List[_1003.GearManufacturingConfigSetupViewModel]':
        '''List[GearManufacturingConfigSetupViewModel]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_1003.GearManufacturingConfigSetupViewModel))
        return value

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
