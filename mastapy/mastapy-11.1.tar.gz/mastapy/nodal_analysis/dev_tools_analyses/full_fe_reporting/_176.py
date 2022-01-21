'''_176.py

ContactPairReporting
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.fe_tools.vis_tools_global.vis_tools_global_enums import _1180, _1179
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONTACT_PAIR_REPORTING = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ContactPairReporting')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactPairReporting',)


class ContactPairReporting(_0.APIBase):
    '''ContactPairReporting

    This is a mastapy class.
    '''

    TYPE = _CONTACT_PAIR_REPORTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ContactPairReporting.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def id(self) -> 'int':
        '''int: 'ID' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ID

    @property
    def reference_surface_type(self) -> '_1180.ContactPairReferenceSurfaceType':
        '''ContactPairReferenceSurfaceType: 'ReferenceSurfaceType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ReferenceSurfaceType)
        return constructor.new(_1180.ContactPairReferenceSurfaceType)(value) if value is not None else None

    @property
    def constrained_surface_type(self) -> '_1179.ContactPairConstrainedSurfaceType':
        '''ContactPairConstrainedSurfaceType: 'ConstrainedSurfaceType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ConstrainedSurfaceType)
        return constructor.new(_1179.ContactPairConstrainedSurfaceType)(value) if value is not None else None

    @property
    def property_id(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'PropertyID' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_int)(self.wrapped.PropertyID) if self.wrapped.PropertyID is not None else None

    @property
    def adjust_distance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AdjustDistance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AdjustDistance) if self.wrapped.AdjustDistance is not None else None

    @adjust_distance.setter
    def adjust_distance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AdjustDistance = value

    @property
    def position_tolerance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PositionTolerance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PositionTolerance) if self.wrapped.PositionTolerance is not None else None

    @position_tolerance.setter
    def position_tolerance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PositionTolerance = value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def swap_reference_and_constrained_surfaces(self):
        ''' 'SwapReferenceAndConstrainedSurfaces' is the original name of this method.'''

        self.wrapped.SwapReferenceAndConstrainedSurfaces()

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
