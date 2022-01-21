'''_9.py

DesignShaftSection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.shafts import _10
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DESIGN_SHAFT_SECTION = python_net_import('SMT.MastaAPI.Shafts', 'DesignShaftSection')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignShaftSection',)


class DesignShaftSection(_0.APIBase):
    '''DesignShaftSection

    This is a mastapy class.
    '''

    TYPE = _DESIGN_SHAFT_SECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignShaftSection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

    @property
    def bore(self) -> 'float':
        '''float: 'Bore' is the original name of this property.'''

        return self.wrapped.Bore

    @bore.setter
    def bore(self, value: 'float'):
        self.wrapped.Bore = float(value) if value else 0.0

    @property
    def torsional_stiffness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TorsionalStiffness' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TorsionalStiffness) if self.wrapped.TorsionalStiffness is not None else None

    @torsional_stiffness.setter
    def torsional_stiffness(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TorsionalStiffness = value

    @property
    def polar_inertia(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PolarInertia' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PolarInertia) if self.wrapped.PolarInertia is not None else None

    @polar_inertia.setter
    def polar_inertia(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PolarInertia = value

    @property
    def left(self) -> '_10.DesignShaftSectionEnd':
        '''DesignShaftSectionEnd: 'Left' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_10.DesignShaftSectionEnd)(self.wrapped.Left) if self.wrapped.Left is not None else None

    @property
    def right(self) -> '_10.DesignShaftSectionEnd':
        '''DesignShaftSectionEnd: 'Right' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_10.DesignShaftSectionEnd)(self.wrapped.Right) if self.wrapped.Right is not None else None

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
