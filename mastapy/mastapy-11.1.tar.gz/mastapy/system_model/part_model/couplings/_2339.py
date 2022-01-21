'''_2339.py

SplineLeadRelief
'''


from typing import List

from mastapy.math_utility.stiffness_calculators import _1335
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.couplings import _2325
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SPLINE_LEAD_RELIEF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SplineLeadRelief')


__docformat__ = 'restructuredtext en'
__all__ = ('SplineLeadRelief',)


class SplineLeadRelief(_0.APIBase):
    '''SplineLeadRelief

    This is a mastapy class.
    '''

    TYPE = _SPLINE_LEAD_RELIEF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SplineLeadRelief.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_position(self) -> '_1335.IndividualContactPosition':
        '''IndividualContactPosition: 'ContactPosition' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ContactPosition)
        return constructor.new(_1335.IndividualContactPosition)(value) if value is not None else None

    @property
    def linear_relief(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LinearRelief' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LinearRelief) if self.wrapped.LinearRelief is not None else None

    @linear_relief.setter
    def linear_relief(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LinearRelief = value

    @property
    def microgeometry_clearance_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'MicrogeometryClearanceChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.MicrogeometryClearanceChart.__class__.__mro__:
            raise CastException('Failed to cast microgeometry_clearance_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.MicrogeometryClearanceChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MicrogeometryClearanceChart.__class__)(self.wrapped.MicrogeometryClearanceChart) if self.wrapped.MicrogeometryClearanceChart is not None else None

    @property
    def crowning(self) -> '_2325.CrowningSpecification':
        '''CrowningSpecification: 'Crowning' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2325.CrowningSpecification)(self.wrapped.Crowning) if self.wrapped.Crowning is not None else None

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
