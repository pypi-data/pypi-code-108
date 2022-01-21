'''_1879.py

BearingDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.math_utility import _1317
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_BEARING_DESIGN = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns', 'BearingDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingDesign',)


class BearingDesign(_0.APIBase):
    '''BearingDesign

    This is a mastapy class.
    '''

    TYPE = _BEARING_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def type_(self) -> 'str':
        '''str: 'Type' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Type

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

    @property
    def bore(self) -> 'float':
        '''float: 'Bore' is the original name of this property.'''

        return self.wrapped.Bore

    @bore.setter
    def bore(self, value: 'float'):
        self.wrapped.Bore = float(value) if value else 0.0

    @property
    def mass(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Mass' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Mass) if self.wrapped.Mass is not None else None

    @mass.setter
    def mass(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Mass = value

    @property
    def total_mass_properties(self) -> '_1317.MassProperties':
        '''MassProperties: 'TotalMassProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1317.MassProperties)(self.wrapped.TotalMassProperties) if self.wrapped.TotalMassProperties is not None else None

    @property
    def mass_properties_of_inner_ring_from_geometry(self) -> '_1317.MassProperties':
        '''MassProperties: 'MassPropertiesOfInnerRingFromGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1317.MassProperties)(self.wrapped.MassPropertiesOfInnerRingFromGeometry) if self.wrapped.MassPropertiesOfInnerRingFromGeometry is not None else None

    @property
    def mass_properties_of_outer_ring_from_geometry(self) -> '_1317.MassProperties':
        '''MassProperties: 'MassPropertiesOfOuterRingFromGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1317.MassProperties)(self.wrapped.MassPropertiesOfOuterRingFromGeometry) if self.wrapped.MassPropertiesOfOuterRingFromGeometry is not None else None

    @property
    def mass_properties_of_elements_from_geometry(self) -> '_1317.MassProperties':
        '''MassProperties: 'MassPropertiesOfElementsFromGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1317.MassProperties)(self.wrapped.MassPropertiesOfElementsFromGeometry) if self.wrapped.MassPropertiesOfElementsFromGeometry is not None else None

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
