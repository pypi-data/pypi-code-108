'''_149.py

RepositionComponentDetails
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_REPOSITION_COMPONENT_DETAILS = python_net_import('SMT.MastaAPI.NodalAnalysis.GeometryModellerLink', 'RepositionComponentDetails')


__docformat__ = 'restructuredtext en'
__all__ = ('RepositionComponentDetails',)


class RepositionComponentDetails(_0.APIBase):
    '''RepositionComponentDetails

    This is a mastapy class.
    '''

    TYPE = _REPOSITION_COMPONENT_DETAILS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RepositionComponentDetails.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def only_move_concentric_components(self) -> 'bool':
        '''bool: 'OnlyMoveConcentricComponents' is the original name of this property.'''

        return self.wrapped.OnlyMoveConcentricComponents

    @only_move_concentric_components.setter
    def only_move_concentric_components(self, value: 'bool'):
        self.wrapped.OnlyMoveConcentricComponents = bool(value) if value else False

    @property
    def reverse_axis_direction(self) -> 'bool':
        '''bool: 'ReverseAxisDirection' is the original name of this property.'''

        return self.wrapped.ReverseAxisDirection

    @reverse_axis_direction.setter
    def reverse_axis_direction(self, value: 'bool'):
        self.wrapped.ReverseAxisDirection = bool(value) if value else False

    @property
    def origin(self) -> 'Vector3D':
        '''Vector3D: 'Origin' is the original name of this property.'''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Origin)
        return value

    @origin.setter
    def origin(self, value: 'Vector3D'):
        value = value if value else None
        value = conversion.mp_to_pn_vector3d(value)
        self.wrapped.Origin = value

    @property
    def direction(self) -> 'Vector3D':
        '''Vector3D: 'Direction' is the original name of this property.'''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Direction)
        return value

    @direction.setter
    def direction(self, value: 'Vector3D'):
        value = value if value else None
        value = conversion.mp_to_pn_vector3d(value)
        self.wrapped.Direction = value

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
