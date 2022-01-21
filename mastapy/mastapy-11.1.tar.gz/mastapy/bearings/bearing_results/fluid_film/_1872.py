'''_1872.py

LoadedPlainJournalBearingRow
'''


from typing import List

from PIL.Image import Image

from mastapy.bearings import _1637
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_LOADED_PLAIN_JOURNAL_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedPlainJournalBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedPlainJournalBearingRow',)


class LoadedPlainJournalBearingRow(_0.APIBase):
    '''LoadedPlainJournalBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_PLAIN_JOURNAL_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedPlainJournalBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def row(self) -> '_1637.BearingRow':
        '''BearingRow: 'Row' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.Row)
        return constructor.new(_1637.BearingRow)(value) if value is not None else None

    @property
    def eccentricity_ratio(self) -> 'float':
        '''float: 'EccentricityRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EccentricityRatio

    @property
    def minimum_film_thickness_at_row_centre(self) -> 'float':
        '''float: 'MinimumFilmThicknessAtRowCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFilmThicknessAtRowCentre

    @property
    def clipped_minimum_film_thickness_at_row_centre(self) -> 'float':
        '''float: 'ClippedMinimumFilmThicknessAtRowCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClippedMinimumFilmThicknessAtRowCentre

    @property
    def angular_position_of_the_minimum_film_thickness_from_the_x_axis(self) -> 'float':
        '''float: 'AngularPositionOfTheMinimumFilmThicknessFromTheXAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularPositionOfTheMinimumFilmThicknessFromTheXAxis

    @property
    def attitude_force(self) -> 'float':
        '''float: 'AttitudeForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AttitudeForce

    @property
    def force_x(self) -> 'float':
        '''float: 'ForceX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceX

    @property
    def force_y(self) -> 'float':
        '''float: 'ForceY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceY

    @property
    def attitude_angle(self) -> 'float':
        '''float: 'AttitudeAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AttitudeAngle

    @property
    def sommerfeld_number(self) -> 'float':
        '''float: 'SommerfeldNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SommerfeldNumber

    @property
    def coefficient_of_traction(self) -> 'float':
        '''float: 'CoefficientOfTraction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CoefficientOfTraction

    @property
    def non_dimensional_load(self) -> 'float':
        '''float: 'NonDimensionalLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalLoad

    @property
    def radial_load_per_unit_of_projected_area(self) -> 'float':
        '''float: 'RadialLoadPerUnitOfProjectedArea' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialLoadPerUnitOfProjectedArea

    @property
    def journal_bearing_loading_chart(self) -> 'Image':
        '''Image: 'JournalBearingLoadingChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.JournalBearingLoadingChart)
        return value

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
