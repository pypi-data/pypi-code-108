'''_39.py

ShaftSurfaceRoughness
'''


from typing import List

from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.shafts import _42
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_SURFACE_ROUGHNESS = python_net_import('SMT.MastaAPI.Shafts', 'ShaftSurfaceRoughness')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftSurfaceRoughness',)


class ShaftSurfaceRoughness(_0.APIBase):
    '''ShaftSurfaceRoughness

    This is a mastapy class.
    '''

    TYPE = _SHAFT_SURFACE_ROUGHNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftSurfaceRoughness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def surface_finish(self) -> 'enum_with_selected_value.EnumWithSelectedValue_SurfaceFinishes':
        '''enum_with_selected_value.EnumWithSelectedValue_SurfaceFinishes: 'SurfaceFinish' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_SurfaceFinishes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.SurfaceFinish, value) if self.wrapped.SurfaceFinish is not None else None

    @surface_finish.setter
    def surface_finish(self, value: 'enum_with_selected_value.EnumWithSelectedValue_SurfaceFinishes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_SurfaceFinishes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.SurfaceFinish = value

    @property
    def surface_roughness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SurfaceRoughness' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SurfaceRoughness) if self.wrapped.SurfaceRoughness is not None else None

    @surface_roughness.setter
    def surface_roughness(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SurfaceRoughness = value

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
