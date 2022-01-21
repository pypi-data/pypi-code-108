'''_57.py

FEMeshingOptions
'''


from typing import List

from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.nodal_analysis import _55, _87, _58
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_MESHING_OPTIONS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'FEMeshingOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('FEMeshingOptions',)


class FEMeshingOptions(_0.APIBase):
    '''FEMeshingOptions

    This is a mastapy class.
    '''

    TYPE = _FE_MESHING_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEMeshingOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def element_size(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementSize' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementSize) if self.wrapped.ElementSize is not None else None

    @element_size.setter
    def element_size(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementSize = value

    @property
    def minimum_element_size(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumElementSize' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumElementSize) if self.wrapped.MinimumElementSize is not None else None

    @minimum_element_size.setter
    def minimum_element_size(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumElementSize = value

    @property
    def element_order(self) -> '_55.ElementOrder':
        '''ElementOrder: 'ElementOrder' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ElementOrder)
        return constructor.new(_55.ElementOrder)(value) if value is not None else None

    @element_order.setter
    def element_order(self, value: '_55.ElementOrder'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ElementOrder = value

    @property
    def element_shape(self) -> '_87.VolumeElementShape':
        '''VolumeElementShape: 'ElementShape' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ElementShape)
        return constructor.new(_87.VolumeElementShape)(value) if value is not None else None

    @element_shape.setter
    def element_shape(self, value: '_87.VolumeElementShape'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ElementShape = value

    @property
    def maximum_spanning_angle(self) -> 'float':
        '''float: 'MaximumSpanningAngle' is the original name of this property.'''

        return self.wrapped.MaximumSpanningAngle

    @maximum_spanning_angle.setter
    def maximum_spanning_angle(self, value: 'float'):
        self.wrapped.MaximumSpanningAngle = float(value) if value else 0.0

    @property
    def maximum_chord_height(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumChordHeight' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumChordHeight) if self.wrapped.MaximumChordHeight is not None else None

    @maximum_chord_height.setter
    def maximum_chord_height(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumChordHeight = value

    @property
    def maximum_growth_rate(self) -> 'float':
        '''float: 'MaximumGrowthRate' is the original name of this property.'''

        return self.wrapped.MaximumGrowthRate

    @maximum_growth_rate.setter
    def maximum_growth_rate(self, value: 'float'):
        self.wrapped.MaximumGrowthRate = float(value) if value else 0.0

    @property
    def minimum_triangle_angle(self) -> 'float':
        '''float: 'MinimumTriangleAngle' is the original name of this property.'''

        return self.wrapped.MinimumTriangleAngle

    @minimum_triangle_angle.setter
    def minimum_triangle_angle(self, value: 'float'):
        self.wrapped.MinimumTriangleAngle = float(value) if value else 0.0

    @property
    def preserve_edge_angle(self) -> 'float':
        '''float: 'PreserveEdgeAngle' is the original name of this property.'''

        return self.wrapped.PreserveEdgeAngle

    @preserve_edge_angle.setter
    def preserve_edge_angle(self, value: 'float'):
        self.wrapped.PreserveEdgeAngle = float(value) if value else 0.0

    @property
    def preserve_node_angle(self) -> 'float':
        '''float: 'PreserveNodeAngle' is the original name of this property.'''

        return self.wrapped.PreserveNodeAngle

    @preserve_node_angle.setter
    def preserve_node_angle(self, value: 'float'):
        self.wrapped.PreserveNodeAngle = float(value) if value else 0.0

    @property
    def maximum_edge_altitude_ratio(self) -> 'float':
        '''float: 'MaximumEdgeAltitudeRatio' is the original name of this property.'''

        return self.wrapped.MaximumEdgeAltitudeRatio

    @maximum_edge_altitude_ratio.setter
    def maximum_edge_altitude_ratio(self, value: 'float'):
        self.wrapped.MaximumEdgeAltitudeRatio = float(value) if value else 0.0

    @property
    def meshing_problems(self) -> 'List[_58.FEMeshingProblem]':
        '''List[FEMeshingProblem]: 'MeshingProblems' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshingProblems, constructor.new(_58.FEMeshingProblem))
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
