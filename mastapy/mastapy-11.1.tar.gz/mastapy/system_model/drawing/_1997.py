'''_1997.py

ScalingDrawStyle
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.utility.enums import _1588
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SCALING_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'ScalingDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('ScalingDrawStyle',)


class ScalingDrawStyle(_0.APIBase):
    '''ScalingDrawStyle

    This is a mastapy class.
    '''

    TYPE = _SCALING_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ScalingDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def scale(self) -> 'float':
        '''float: 'Scale' is the original name of this property.'''

        return self.wrapped.Scale

    @scale.setter
    def scale(self, value: 'float'):
        self.wrapped.Scale = float(value) if value else 0.0

    @property
    def bearing_force_arrows(self) -> '_1588.BearingForceArrowOption':
        '''BearingForceArrowOption: 'BearingForceArrows' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.BearingForceArrows)
        return constructor.new(_1588.BearingForceArrowOption)(value) if value is not None else None

    @bearing_force_arrows.setter
    def bearing_force_arrows(self, value: '_1588.BearingForceArrowOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.BearingForceArrows = value

    @property
    def max_scale(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaxScale' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaxScale) if self.wrapped.MaxScale is not None else None

    @max_scale.setter
    def max_scale(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaxScale = value

    @property
    def min_scale(self) -> 'float':
        '''float: 'MinScale' is the original name of this property.'''

        return self.wrapped.MinScale

    @min_scale.setter
    def min_scale(self, value: 'float'):
        self.wrapped.MinScale = float(value) if value else 0.0

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
