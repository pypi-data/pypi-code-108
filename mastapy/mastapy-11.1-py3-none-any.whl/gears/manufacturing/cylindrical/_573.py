'''_573.py

CylindricalGearSpecifiedMicroGeometry
'''


from typing import List

from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _605
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears.manufacturing.cylindrical import _594, _595
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SPECIFIED_MICRO_GEOMETRY = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'CylindricalGearSpecifiedMicroGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSpecifiedMicroGeometry',)


class CylindricalGearSpecifiedMicroGeometry(_0.APIBase):
    '''CylindricalGearSpecifiedMicroGeometry

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SPECIFIED_MICRO_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSpecifiedMicroGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def lead_measurement_method(self) -> '_605.MicroGeometryDefinitionMethod':
        '''MicroGeometryDefinitionMethod: 'LeadMeasurementMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LeadMeasurementMethod)
        return constructor.new(_605.MicroGeometryDefinitionMethod)(value) if value is not None else None

    @lead_measurement_method.setter
    def lead_measurement_method(self, value: '_605.MicroGeometryDefinitionMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LeadMeasurementMethod = value

    @property
    def profile_measurement_method(self) -> '_605.MicroGeometryDefinitionMethod':
        '''MicroGeometryDefinitionMethod: 'ProfileMeasurementMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ProfileMeasurementMethod)
        return constructor.new(_605.MicroGeometryDefinitionMethod)(value) if value is not None else None

    @profile_measurement_method.setter
    def profile_measurement_method(self, value: '_605.MicroGeometryDefinitionMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ProfileMeasurementMethod = value

    @property
    def number_of_transverse_planes(self) -> 'int':
        '''int: 'NumberOfTransversePlanes' is the original name of this property.'''

        return self.wrapped.NumberOfTransversePlanes

    @number_of_transverse_planes.setter
    def number_of_transverse_planes(self, value: 'int'):
        self.wrapped.NumberOfTransversePlanes = int(value) if value else 0

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def lead_micro_geometry(self) -> '_594.MicroGeometryInputsLead':
        '''MicroGeometryInputsLead: 'LeadMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_594.MicroGeometryInputsLead)(self.wrapped.LeadMicroGeometry) if self.wrapped.LeadMicroGeometry is not None else None

    @property
    def profile_micro_geometry(self) -> 'List[_595.MicroGeometryInputsProfile]':
        '''List[MicroGeometryInputsProfile]: 'ProfileMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ProfileMicroGeometry, constructor.new(_595.MicroGeometryInputsProfile))
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
