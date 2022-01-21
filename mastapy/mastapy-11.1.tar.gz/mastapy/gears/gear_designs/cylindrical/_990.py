'''_990.py

CylindricalGearToothThicknessSpecification
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_TOOTH_THICKNESS_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearToothThicknessSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearToothThicknessSpecification',)


TMeasurement = TypeVar('TMeasurement', bound='_1398.MeasurementBase')


class CylindricalGearToothThicknessSpecification(_0.APIBase, Generic[TMeasurement]):
    '''CylindricalGearToothThicknessSpecification

    This is a mastapy class.

    Generic Types:
        TMeasurement
    '''

    TYPE = _CYLINDRICAL_GEAR_TOOTH_THICKNESS_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearToothThicknessSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def thickness_measurement_type(self) -> 'str':
        '''str: 'ThicknessMeasurementType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThicknessMeasurementType

    @property
    def minimum_thickness_reduction(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumThicknessReduction' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumThicknessReduction) if self.wrapped.MinimumThicknessReduction is not None else None

    @minimum_thickness_reduction.setter
    def minimum_thickness_reduction(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumThicknessReduction = value

    @property
    def tolerance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Tolerance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Tolerance) if self.wrapped.Tolerance is not None else None

    @tolerance.setter
    def tolerance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Tolerance = value

    @property
    def nominal_zero_backlash(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NominalZeroBacklash' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NominalZeroBacklash) if self.wrapped.NominalZeroBacklash is not None else None

    @nominal_zero_backlash.setter
    def nominal_zero_backlash(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NominalZeroBacklash = value

    @property
    def maximum_metal(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumMetal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumMetal) if self.wrapped.MaximumMetal is not None else None

    @maximum_metal.setter
    def maximum_metal(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumMetal = value

    @property
    def average_mean_metal(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AverageMeanMetal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AverageMeanMetal) if self.wrapped.AverageMeanMetal is not None else None

    @average_mean_metal.setter
    def average_mean_metal(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AverageMeanMetal = value

    @property
    def minimum_metal(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumMetal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumMetal) if self.wrapped.MinimumMetal is not None else None

    @minimum_metal.setter
    def minimum_metal(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumMetal = value

    @property
    def upper_allowance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'UpperAllowance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.UpperAllowance) if self.wrapped.UpperAllowance is not None else None

    @upper_allowance.setter
    def upper_allowance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.UpperAllowance = value

    @property
    def lower_allowance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LowerAllowance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LowerAllowance) if self.wrapped.LowerAllowance is not None else None

    @lower_allowance.setter
    def lower_allowance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LowerAllowance = value

    @property
    def average_allowance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AverageAllowance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AverageAllowance) if self.wrapped.AverageAllowance is not None else None

    @average_allowance.setter
    def average_allowance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AverageAllowance = value

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
