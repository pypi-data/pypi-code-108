'''_7041.py

CylindricalMeshedGearAdvancedSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7038, _7042, _7039
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MESHED_GEAR_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'CylindricalMeshedGearAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshedGearAdvancedSystemDeflection',)


class CylindricalMeshedGearAdvancedSystemDeflection(_0.APIBase):
    '''CylindricalMeshedGearAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESHED_GEAR_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshedGearAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mean_node_torque_in_meshes(self) -> 'float':
        '''float: 'MeanNodeTorqueInMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanNodeTorqueInMeshes

    @property
    def maximum_von_mises_root_stress_tension(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressTension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressTension

    @property
    def maximum_principal_root_stress_tension(self) -> 'float':
        '''float: 'MaximumPrincipalRootStressTension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalRootStressTension

    @property
    def maximum_von_mises_root_stress_compression(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressCompression' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressCompression

    @property
    def maximum_principal_root_stress_compression(self) -> 'float':
        '''float: 'MaximumPrincipalRootStressCompression' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalRootStressCompression

    @property
    def cylindrical_gear_advanced_system_deflection(self) -> '_7038.CylindricalGearAdvancedSystemDeflection':
        '''CylindricalGearAdvancedSystemDeflection: 'CylindricalGearAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _7038.CylindricalGearAdvancedSystemDeflection.TYPE not in self.wrapped.CylindricalGearAdvancedSystemDeflection.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_advanced_system_deflection to CylindricalGearAdvancedSystemDeflection. Expected: {}.'.format(self.wrapped.CylindricalGearAdvancedSystemDeflection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearAdvancedSystemDeflection.__class__)(self.wrapped.CylindricalGearAdvancedSystemDeflection) if self.wrapped.CylindricalGearAdvancedSystemDeflection is not None else None

    @property
    def other_cylindrical_gear_advanced_system_deflection(self) -> '_7038.CylindricalGearAdvancedSystemDeflection':
        '''CylindricalGearAdvancedSystemDeflection: 'OtherCylindricalGearAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _7038.CylindricalGearAdvancedSystemDeflection.TYPE not in self.wrapped.OtherCylindricalGearAdvancedSystemDeflection.__class__.__mro__:
            raise CastException('Failed to cast other_cylindrical_gear_advanced_system_deflection to CylindricalGearAdvancedSystemDeflection. Expected: {}.'.format(self.wrapped.OtherCylindricalGearAdvancedSystemDeflection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OtherCylindricalGearAdvancedSystemDeflection.__class__)(self.wrapped.OtherCylindricalGearAdvancedSystemDeflection) if self.wrapped.OtherCylindricalGearAdvancedSystemDeflection is not None else None

    @property
    def cylindrical_gear_mesh_advanced_system_deflection(self) -> '_7039.CylindricalGearMeshAdvancedSystemDeflection':
        '''CylindricalGearMeshAdvancedSystemDeflection: 'CylindricalGearMeshAdvancedSystemDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_7039.CylindricalGearMeshAdvancedSystemDeflection)(self.wrapped.CylindricalGearMeshAdvancedSystemDeflection) if self.wrapped.CylindricalGearMeshAdvancedSystemDeflection is not None else None

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
