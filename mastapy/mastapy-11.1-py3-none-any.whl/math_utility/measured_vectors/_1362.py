'''_1362.py

OverridableDisplacementBoundaryCondition
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OVERRIDABLE_DISPLACEMENT_BOUNDARY_CONDITION = python_net_import('SMT.MastaAPI.MathUtility.MeasuredVectors', 'OverridableDisplacementBoundaryCondition')


__docformat__ = 'restructuredtext en'
__all__ = ('OverridableDisplacementBoundaryCondition',)


class OverridableDisplacementBoundaryCondition(_0.APIBase):
    '''OverridableDisplacementBoundaryCondition

    This is a mastapy class.
    '''

    TYPE = _OVERRIDABLE_DISPLACEMENT_BOUNDARY_CONDITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OverridableDisplacementBoundaryCondition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'X' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.X) if self.wrapped.X is not None else None

    @x.setter
    def x(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.X = value

    @property
    def y(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Y' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Y) if self.wrapped.Y is not None else None

    @y.setter
    def y(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Y = value

    @property
    def z(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Z' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Z) if self.wrapped.Z is not None else None

    @z.setter
    def z(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Z = value

    @property
    def theta_x(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ThetaX' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ThetaX) if self.wrapped.ThetaX is not None else None

    @theta_x.setter
    def theta_x(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ThetaX = value

    @property
    def theta_y(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ThetaY' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ThetaY) if self.wrapped.ThetaY is not None else None

    @theta_y.setter
    def theta_y(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ThetaY = value

    @property
    def theta_z(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ThetaZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ThetaZ) if self.wrapped.ThetaZ is not None else None

    @theta_z.setter
    def theta_z(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ThetaZ = value

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

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
