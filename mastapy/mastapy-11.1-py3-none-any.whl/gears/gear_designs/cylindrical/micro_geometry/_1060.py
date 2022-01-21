'''_1060.py

CylindricalGearTriangularEndModificationAtOrientation
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1078, _1066, _1073
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_TRIANGULAR_END_MODIFICATION_AT_ORIENTATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearTriangularEndModificationAtOrientation')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearTriangularEndModificationAtOrientation',)


class CylindricalGearTriangularEndModificationAtOrientation(_0.APIBase):
    '''CylindricalGearTriangularEndModificationAtOrientation

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_TRIANGULAR_END_MODIFICATION_AT_ORIENTATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearTriangularEndModificationAtOrientation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def orientation(self) -> 'str':
        '''str: 'Orientation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Orientation

    @property
    def linear(self) -> '_1078.SingleCylindricalGearTriangularEndModification':
        '''SingleCylindricalGearTriangularEndModification: 'Linear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1078.SingleCylindricalGearTriangularEndModification.TYPE not in self.wrapped.Linear.__class__.__mro__:
            raise CastException('Failed to cast linear to SingleCylindricalGearTriangularEndModification. Expected: {}.'.format(self.wrapped.Linear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Linear.__class__)(self.wrapped.Linear) if self.wrapped.Linear is not None else None

    @property
    def linear_of_type_linear_cylindrical_gear_triangular_end_modification(self) -> '_1066.LinearCylindricalGearTriangularEndModification':
        '''LinearCylindricalGearTriangularEndModification: 'Linear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1066.LinearCylindricalGearTriangularEndModification.TYPE not in self.wrapped.Linear.__class__.__mro__:
            raise CastException('Failed to cast linear to LinearCylindricalGearTriangularEndModification. Expected: {}.'.format(self.wrapped.Linear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Linear.__class__)(self.wrapped.Linear) if self.wrapped.Linear is not None else None

    @property
    def linear_of_type_parabolic_cylindrical_gear_triangular_end_modification(self) -> '_1073.ParabolicCylindricalGearTriangularEndModification':
        '''ParabolicCylindricalGearTriangularEndModification: 'Linear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1073.ParabolicCylindricalGearTriangularEndModification.TYPE not in self.wrapped.Linear.__class__.__mro__:
            raise CastException('Failed to cast linear to ParabolicCylindricalGearTriangularEndModification. Expected: {}.'.format(self.wrapped.Linear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Linear.__class__)(self.wrapped.Linear) if self.wrapped.Linear is not None else None

    @property
    def parabolic(self) -> '_1078.SingleCylindricalGearTriangularEndModification':
        '''SingleCylindricalGearTriangularEndModification: 'Parabolic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1078.SingleCylindricalGearTriangularEndModification.TYPE not in self.wrapped.Parabolic.__class__.__mro__:
            raise CastException('Failed to cast parabolic to SingleCylindricalGearTriangularEndModification. Expected: {}.'.format(self.wrapped.Parabolic.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Parabolic.__class__)(self.wrapped.Parabolic) if self.wrapped.Parabolic is not None else None

    @property
    def parabolic_of_type_linear_cylindrical_gear_triangular_end_modification(self) -> '_1066.LinearCylindricalGearTriangularEndModification':
        '''LinearCylindricalGearTriangularEndModification: 'Parabolic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1066.LinearCylindricalGearTriangularEndModification.TYPE not in self.wrapped.Parabolic.__class__.__mro__:
            raise CastException('Failed to cast parabolic to LinearCylindricalGearTriangularEndModification. Expected: {}.'.format(self.wrapped.Parabolic.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Parabolic.__class__)(self.wrapped.Parabolic) if self.wrapped.Parabolic is not None else None

    @property
    def parabolic_of_type_parabolic_cylindrical_gear_triangular_end_modification(self) -> '_1073.ParabolicCylindricalGearTriangularEndModification':
        '''ParabolicCylindricalGearTriangularEndModification: 'Parabolic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1073.ParabolicCylindricalGearTriangularEndModification.TYPE not in self.wrapped.Parabolic.__class__.__mro__:
            raise CastException('Failed to cast parabolic to ParabolicCylindricalGearTriangularEndModification. Expected: {}.'.format(self.wrapped.Parabolic.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Parabolic.__class__)(self.wrapped.Parabolic) if self.wrapped.Parabolic is not None else None

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
