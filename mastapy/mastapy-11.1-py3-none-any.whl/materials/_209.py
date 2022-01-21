'''_209.py

AcousticRadiationEfficiency
'''


from typing import List

from mastapy.math_utility import _1333
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.materials import _210
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ACOUSTIC_RADIATION_EFFICIENCY = python_net_import('SMT.MastaAPI.Materials', 'AcousticRadiationEfficiency')


__docformat__ = 'restructuredtext en'
__all__ = ('AcousticRadiationEfficiency',)


class AcousticRadiationEfficiency(_0.APIBase):
    '''AcousticRadiationEfficiency

    This is a mastapy class.
    '''

    TYPE = _ACOUSTIC_RADIATION_EFFICIENCY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AcousticRadiationEfficiency.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radiation_efficiency_curve(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'RadiationEfficiencyCurve' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.RadiationEfficiencyCurve) if self.wrapped.RadiationEfficiencyCurve is not None else None

    @radiation_efficiency_curve.setter
    def radiation_efficiency_curve(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.RadiationEfficiencyCurve = value

    @property
    def input_type(self) -> '_210.AcousticRadiationEfficiencyInputType':
        '''AcousticRadiationEfficiencyInputType: 'InputType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.InputType)
        return constructor.new(_210.AcousticRadiationEfficiencyInputType)(value) if value is not None else None

    @input_type.setter
    def input_type(self, value: '_210.AcousticRadiationEfficiencyInputType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.InputType = value

    @property
    def knee_frequency(self) -> 'float':
        '''float: 'KneeFrequency' is the original name of this property.'''

        return self.wrapped.KneeFrequency

    @knee_frequency.setter
    def knee_frequency(self, value: 'float'):
        self.wrapped.KneeFrequency = float(value) if value else 0.0

    @property
    def low_frequency_power(self) -> 'float':
        '''float: 'LowFrequencyPower' is the original name of this property.'''

        return self.wrapped.LowFrequencyPower

    @low_frequency_power.setter
    def low_frequency_power(self, value: 'float'):
        self.wrapped.LowFrequencyPower = float(value) if value else 0.0

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
