'''_1369.py

GaussKronrodOptions
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GAUSS_KRONROD_OPTIONS = python_net_import('SMT.MastaAPI.MathUtility.Integration', 'GaussKronrodOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('GaussKronrodOptions',)


class GaussKronrodOptions(_0.APIBase):
    '''GaussKronrodOptions

    This is a mastapy class.
    '''

    TYPE = _GAUSS_KRONROD_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GaussKronrodOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_advanced_zero_region_detection_when_subdividing_domains(self) -> 'bool':
        '''bool: 'UseAdvancedZeroRegionDetectionWhenSubdividingDomains' is the original name of this property.'''

        return self.wrapped.UseAdvancedZeroRegionDetectionWhenSubdividingDomains

    @use_advanced_zero_region_detection_when_subdividing_domains.setter
    def use_advanced_zero_region_detection_when_subdividing_domains(self, value: 'bool'):
        self.wrapped.UseAdvancedZeroRegionDetectionWhenSubdividingDomains = bool(value) if value else False

    @property
    def pre_scan_domains_for_endpoint_zero_regions(self) -> 'bool':
        '''bool: 'PreScanDomainsForEndpointZeroRegions' is the original name of this property.'''

        return self.wrapped.PreScanDomainsForEndpointZeroRegions

    @pre_scan_domains_for_endpoint_zero_regions.setter
    def pre_scan_domains_for_endpoint_zero_regions(self, value: 'bool'):
        self.wrapped.PreScanDomainsForEndpointZeroRegions = bool(value) if value else False

    @property
    def number_of_sample_points_when_finding_zero_regions(self) -> 'int':
        '''int: 'NumberOfSamplePointsWhenFindingZeroRegions' is the original name of this property.'''

        return self.wrapped.NumberOfSamplePointsWhenFindingZeroRegions

    @number_of_sample_points_when_finding_zero_regions.setter
    def number_of_sample_points_when_finding_zero_regions(self, value: 'int'):
        self.wrapped.NumberOfSamplePointsWhenFindingZeroRegions = int(value) if value else 0

    @property
    def precision_for_refining_zero_regions(self) -> 'float':
        '''float: 'PrecisionForRefiningZeroRegions' is the original name of this property.'''

        return self.wrapped.PrecisionForRefiningZeroRegions

    @precision_for_refining_zero_regions.setter
    def precision_for_refining_zero_regions(self, value: 'float'):
        self.wrapped.PrecisionForRefiningZeroRegions = float(value) if value else 0.0

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
