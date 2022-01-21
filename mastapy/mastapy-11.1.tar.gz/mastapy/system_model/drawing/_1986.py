'''_1986.py

ConcentricPartGroupCombinationSystemDeflectionShaftResults
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2539
from mastapy._internal import constructor, conversion
from mastapy.system_model.drawing import _1998
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONCENTRIC_PART_GROUP_COMBINATION_SYSTEM_DEFLECTION_SHAFT_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'ConcentricPartGroupCombinationSystemDeflectionShaftResults')


__docformat__ = 'restructuredtext en'
__all__ = ('ConcentricPartGroupCombinationSystemDeflectionShaftResults',)


class ConcentricPartGroupCombinationSystemDeflectionShaftResults(_0.APIBase):
    '''ConcentricPartGroupCombinationSystemDeflectionShaftResults

    This is a mastapy class.
    '''

    TYPE = _CONCENTRIC_PART_GROUP_COMBINATION_SYSTEM_DEFLECTION_SHAFT_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConcentricPartGroupCombinationSystemDeflectionShaftResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaft_system_deflection(self) -> '_2539.ShaftSystemDeflection':
        '''ShaftSystemDeflection: 'ShaftSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2539.ShaftSystemDeflection)(self.wrapped.ShaftSystemDeflection) if self.wrapped.ShaftSystemDeflection is not None else None

    @property
    def node_results(self) -> 'List[_1998.ShaftDeflectionDrawingNodeItem]':
        '''List[ShaftDeflectionDrawingNodeItem]: 'NodeResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.NodeResults, constructor.new(_1998.ShaftDeflectionDrawingNodeItem))
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
