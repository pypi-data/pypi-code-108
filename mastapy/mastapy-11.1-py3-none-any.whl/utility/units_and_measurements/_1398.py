'''_1398.py

MeasurementBase
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import list_with_selected_item, overridable
from mastapy.utility.units_and_measurements import (
    _1403, _1395, _1396, _1397,
    _1401, _1402, _1404
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility import _1391
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_BASE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements', 'MeasurementBase')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementBase',)


class MeasurementBase(_0.APIBase):
    '''MeasurementBase

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementBase.TYPE'):
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
    def default_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'DefaultUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.DefaultUnit) if self.wrapped.DefaultUnit is not None else None

    @default_unit.setter
    def default_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.DefaultUnit = value

    @property
    def rounding_digits(self) -> 'int':
        '''int: 'RoundingDigits' is the original name of this property.'''

        return self.wrapped.RoundingDigits

    @rounding_digits.setter
    def rounding_digits(self, value: 'int'):
        self.wrapped.RoundingDigits = int(value) if value else 0

    @property
    def rounding_method(self) -> '_1391.RoundingMethods':
        '''RoundingMethods: 'RoundingMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.RoundingMethod)
        return constructor.new(_1391.RoundingMethods)(value) if value is not None else None

    @rounding_method.setter
    def rounding_method(self, value: '_1391.RoundingMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.RoundingMethod = value

    @property
    def absolute_tolerance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AbsoluteTolerance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AbsoluteTolerance) if self.wrapped.AbsoluteTolerance is not None else None

    @absolute_tolerance.setter
    def absolute_tolerance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AbsoluteTolerance = value

    @property
    def percentage_tolerance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PercentageTolerance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PercentageTolerance) if self.wrapped.PercentageTolerance is not None else None

    @percentage_tolerance.setter
    def percentage_tolerance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PercentageTolerance = value

    @property
    def current_unit(self) -> '_1403.Unit':
        '''Unit: 'CurrentUnit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1403.Unit.TYPE not in self.wrapped.CurrentUnit.__class__.__mro__:
            raise CastException('Failed to cast current_unit to Unit. Expected: {}.'.format(self.wrapped.CurrentUnit.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CurrentUnit.__class__)(self.wrapped.CurrentUnit) if self.wrapped.CurrentUnit is not None else None

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
