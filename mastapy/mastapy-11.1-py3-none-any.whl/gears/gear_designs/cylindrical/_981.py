'''_981.py

CylindricalGearProfileMeasurement
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_PROFILE_MEASUREMENT = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearProfileMeasurement')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearProfileMeasurement',)


class CylindricalGearProfileMeasurement(_0.APIBase):
    '''CylindricalGearProfileMeasurement

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_PROFILE_MEASUREMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearProfileMeasurement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def rolling_distance(self) -> 'float':
        '''float: 'RollingDistance' is the original name of this property.'''

        return self.wrapped.RollingDistance

    @rolling_distance.setter
    def rolling_distance(self, value: 'float'):
        self.wrapped.RollingDistance = float(value) if value else 0.0

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0

    @property
    def roll_angle(self) -> 'float':
        '''float: 'RollAngle' is the original name of this property.'''

        return self.wrapped.RollAngle

    @roll_angle.setter
    def roll_angle(self, value: 'float'):
        self.wrapped.RollAngle = float(value) if value else 0.0

    @property
    def signed_diameter(self) -> 'float':
        '''float: 'SignedDiameter' is the original name of this property.'''

        return self.wrapped.SignedDiameter

    @signed_diameter.setter
    def signed_diameter(self, value: 'float'):
        self.wrapped.SignedDiameter = float(value) if value else 0.0

    @property
    def auto_diameter_show_depending_on_settings(self) -> 'float':
        '''float: 'AutoDiameterShowDependingOnSettings' is the original name of this property.'''

        return self.wrapped.AutoDiameterShowDependingOnSettings

    @auto_diameter_show_depending_on_settings.setter
    def auto_diameter_show_depending_on_settings(self, value: 'float'):
        self.wrapped.AutoDiameterShowDependingOnSettings = float(value) if value else 0.0

    @property
    def auto_radius_show_depending_on_settings(self) -> 'float':
        '''float: 'AutoRadiusShowDependingOnSettings' is the original name of this property.'''

        return self.wrapped.AutoRadiusShowDependingOnSettings

    @auto_radius_show_depending_on_settings.setter
    def auto_radius_show_depending_on_settings(self, value: 'float'):
        self.wrapped.AutoRadiusShowDependingOnSettings = float(value) if value else 0.0

    @property
    def auto_rolling_distance_show_depending_on_settings(self) -> 'float':
        '''float: 'AutoRollingDistanceShowDependingOnSettings' is the original name of this property.'''

        return self.wrapped.AutoRollingDistanceShowDependingOnSettings

    @auto_rolling_distance_show_depending_on_settings.setter
    def auto_rolling_distance_show_depending_on_settings(self, value: 'float'):
        self.wrapped.AutoRollingDistanceShowDependingOnSettings = float(value) if value else 0.0

    @property
    def auto_roll_angle_show_depending_on_settings(self) -> 'float':
        '''float: 'AutoRollAngleShowDependingOnSettings' is the original name of this property.'''

        return self.wrapped.AutoRollAngleShowDependingOnSettings

    @auto_roll_angle_show_depending_on_settings.setter
    def auto_roll_angle_show_depending_on_settings(self, value: 'float'):
        self.wrapped.AutoRollAngleShowDependingOnSettings = float(value) if value else 0.0

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
