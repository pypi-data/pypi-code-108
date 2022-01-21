'''_721.py

RedressingSettings
'''


from typing import List, Generic, TypeVar

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.manufacturing.cylindrical.cutters import _693, _688
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _725
from mastapy._internal.python_net import python_net_import

_REDRESSING_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'RedressingSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('RedressingSettings',)


T = TypeVar('T', bound='_725.ShavingDynamics')


class RedressingSettings(_0.APIBase, Generic[T]):
    '''RedressingSettings

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _REDRESSING_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RedressingSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def selected(self) -> 'bool':
        '''bool: 'Selected' is the original name of this property.'''

        return self.wrapped.Selected

    @selected.setter
    def selected(self, value: 'bool'):
        self.wrapped.Selected = bool(value) if value else False

    @property
    def normal_thickness_at_reference_diameter(self) -> 'float':
        '''float: 'NormalThicknessAtReferenceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThicknessAtReferenceDiameter

    @property
    def shaver_tip_diameter(self) -> 'float':
        '''float: 'ShaverTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverTipDiameter

    @property
    def shaft_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ShaftAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ShaftAngle) if self.wrapped.ShaftAngle is not None else None

    @shaft_angle.setter
    def shaft_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ShaftAngle = value

    @property
    def centre_distance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CentreDistance) if self.wrapped.CentreDistance is not None else None

    @property
    def operating_normal_pressure_angle(self) -> 'float':
        '''float: 'OperatingNormalPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OperatingNormalPressureAngle

    @property
    def shaver_tip_thickness(self) -> 'float':
        '''float: 'ShaverTipThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverTipThickness

    @property
    def icon(self) -> 'Image':
        '''Image: 'Icon' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.Icon)
        return value

    @property
    def shaving_status(self) -> 'str':
        '''str: 'ShavingStatus' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShavingStatus

    @property
    def shaver_minimum_sap_diameter(self) -> 'float':
        '''float: 'ShaverMinimumSAPDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverMinimumSAPDiameter

    @property
    def shaver_maximum_eap_diameter(self) -> 'float':
        '''float: 'ShaverMaximumEAPDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverMaximumEAPDiameter

    @property
    def redressed_shaver(self) -> '_693.CylindricalGearShaver':
        '''CylindricalGearShaver: 'RedressedShaver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _693.CylindricalGearShaver.TYPE not in self.wrapped.RedressedShaver.__class__.__mro__:
            raise CastException('Failed to cast redressed_shaver to CylindricalGearShaver. Expected: {}.'.format(self.wrapped.RedressedShaver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RedressedShaver.__class__)(self.wrapped.RedressedShaver) if self.wrapped.RedressedShaver is not None else None

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
