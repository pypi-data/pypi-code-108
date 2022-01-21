'''_153.py

DrawStyleForFE
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.nodal_analysis import _56
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DRAW_STYLE_FOR_FE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'DrawStyleForFE')


__docformat__ = 'restructuredtext en'
__all__ = ('DrawStyleForFE',)


class DrawStyleForFE(_0.APIBase):
    '''DrawStyleForFE

    This is a mastapy class.
    '''

    TYPE = _DRAW_STYLE_FOR_FE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DrawStyleForFE.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def node_size(self) -> 'int':
        '''int: 'NodeSize' is the original name of this property.'''

        return self.wrapped.NodeSize

    @node_size.setter
    def node_size(self, value: 'int'):
        self.wrapped.NodeSize = int(value) if value else 0

    @property
    def line_option(self) -> '_56.FEMeshElementEntityOption':
        '''FEMeshElementEntityOption: 'LineOption' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LineOption)
        return constructor.new(_56.FEMeshElementEntityOption)(value) if value is not None else None

    @line_option.setter
    def line_option(self, value: '_56.FEMeshElementEntityOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LineOption = value

    @property
    def grounded_nodes(self) -> 'bool':
        '''bool: 'GroundedNodes' is the original name of this property.'''

        return self.wrapped.GroundedNodes

    @grounded_nodes.setter
    def grounded_nodes(self, value: 'bool'):
        self.wrapped.GroundedNodes = bool(value) if value else False

    @property
    def rigid_elements(self) -> 'bool':
        '''bool: 'RigidElements' is the original name of this property.'''

        return self.wrapped.RigidElements

    @rigid_elements.setter
    def rigid_elements(self, value: 'bool'):
        self.wrapped.RigidElements = bool(value) if value else False

    @property
    def highlight_bad_elements(self) -> 'bool':
        '''bool: 'HighlightBadElements' is the original name of this property.'''

        return self.wrapped.HighlightBadElements

    @highlight_bad_elements.setter
    def highlight_bad_elements(self, value: 'bool'):
        self.wrapped.HighlightBadElements = bool(value) if value else False

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
