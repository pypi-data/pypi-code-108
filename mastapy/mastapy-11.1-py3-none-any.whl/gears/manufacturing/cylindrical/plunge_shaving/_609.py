'''_609.py

PlungeShaverGeneration
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1287
from mastapy.math_utility.measured_ranges import _1364
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical import _961
from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _616, _602
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLUNGE_SHAVER_GENERATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'PlungeShaverGeneration')


__docformat__ = 'restructuredtext en'
__all__ = ('PlungeShaverGeneration',)


class PlungeShaverGeneration(_0.APIBase):
    '''PlungeShaverGeneration

    This is a mastapy class.
    '''

    TYPE = _PLUNGE_SHAVER_GENERATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlungeShaverGeneration.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaft_angle_unsigned(self) -> 'float':
        '''float: 'ShaftAngleUnsigned' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftAngleUnsigned

    @property
    def gear_start_of_active_profile_diameter(self) -> 'float':
        '''float: 'GearStartOfActiveProfileDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearStartOfActiveProfileDiameter

    @property
    def manufactured_end_of_active_profile_diameter(self) -> 'float':
        '''float: 'ManufacturedEndOfActiveProfileDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ManufacturedEndOfActiveProfileDiameter

    @property
    def manufactured_start_of_active_profile_diameter(self) -> 'float':
        '''float: 'ManufacturedStartOfActiveProfileDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ManufacturedStartOfActiveProfileDiameter

    @property
    def calculated_conjugate_face_width(self) -> '_1287.Range':
        '''Range: 'CalculatedConjugateFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1287.Range.TYPE not in self.wrapped.CalculatedConjugateFaceWidth.__class__.__mro__:
            raise CastException('Failed to cast calculated_conjugate_face_width to Range. Expected: {}.'.format(self.wrapped.CalculatedConjugateFaceWidth.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CalculatedConjugateFaceWidth.__class__)(self.wrapped.CalculatedConjugateFaceWidth) if self.wrapped.CalculatedConjugateFaceWidth is not None else None

    @property
    def crossed_axis_calculation_details(self) -> '_961.CrossedAxisCylindricalGearPairLineContact':
        '''CrossedAxisCylindricalGearPairLineContact: 'CrossedAxisCalculationDetails' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_961.CrossedAxisCylindricalGearPairLineContact)(self.wrapped.CrossedAxisCalculationDetails) if self.wrapped.CrossedAxisCalculationDetails is not None else None

    @property
    def points_of_interest_on_the_shaver(self) -> 'List[_616.ShaverPointOfInterest]':
        '''List[ShaverPointOfInterest]: 'PointsOfInterestOnTheShaver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PointsOfInterestOnTheShaver, constructor.new(_616.ShaverPointOfInterest))
        return value

    @property
    def calculation_errors(self) -> 'List[_602.CalculationError]':
        '''List[CalculationError]: 'CalculationErrors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CalculationErrors, constructor.new(_602.CalculationError))
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
