'''_62.py

FEStiffness
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.nodal_analysis import _74
from mastapy._math.vector_3d import Vector3D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_STIFFNESS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'FEStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('FEStiffness',)


class FEStiffness(_0.APIBase):
    '''FEStiffness

    This is a mastapy class.
    '''

    TYPE = _FE_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radial_alignment_tolerance(self) -> 'float':
        '''float: 'RadialAlignmentTolerance' is the original name of this property.'''

        return self.wrapped.RadialAlignmentTolerance

    @radial_alignment_tolerance.setter
    def radial_alignment_tolerance(self, value: 'float'):
        self.wrapped.RadialAlignmentTolerance = float(value) if value else 0.0

    @property
    def axial_alignment_tolerance(self) -> 'float':
        '''float: 'AxialAlignmentTolerance' is the original name of this property.'''

        return self.wrapped.AxialAlignmentTolerance

    @axial_alignment_tolerance.setter
    def axial_alignment_tolerance(self, value: 'float'):
        self.wrapped.AxialAlignmentTolerance = float(value) if value else 0.0

    @property
    def is_grounded(self) -> 'bool':
        '''bool: 'IsGrounded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsGrounded

    @property
    def tolerance_for_zero_frequencies(self) -> 'float':
        '''float: 'ToleranceForZeroFrequencies' is the original name of this property.'''

        return self.wrapped.ToleranceForZeroFrequencies

    @tolerance_for_zero_frequencies.setter
    def tolerance_for_zero_frequencies(self, value: 'float'):
        self.wrapped.ToleranceForZeroFrequencies = float(value) if value else 0.0

    @property
    def mass_matrix_is_known(self) -> 'bool':
        '''bool: 'MassMatrixIsKnown' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassMatrixIsKnown

    @property
    def gyroscopic_matrix_is_known(self) -> 'bool':
        '''bool: 'GyroscopicMatrixIsKnown' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GyroscopicMatrixIsKnown

    @property
    def number_of_physical_nodes(self) -> 'int':
        '''int: 'NumberOfPhysicalNodes' is the original name of this property.'''

        return self.wrapped.NumberOfPhysicalNodes

    @number_of_physical_nodes.setter
    def number_of_physical_nodes(self, value: 'int'):
        self.wrapped.NumberOfPhysicalNodes = int(value) if value else 0

    @property
    def number_of_internal_modes(self) -> 'int':
        '''int: 'NumberOfInternalModes' is the original name of this property.'''

        return self.wrapped.NumberOfInternalModes

    @number_of_internal_modes.setter
    def number_of_internal_modes(self, value: 'int'):
        self.wrapped.NumberOfInternalModes = int(value) if value else 0

    @property
    def frequency_of_highest_mode(self) -> 'float':
        '''float: 'FrequencyOfHighestMode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrequencyOfHighestMode

    @property
    def reason_scalar_mass_not_known(self) -> 'str':
        '''str: 'ReasonScalarMassNotKnown' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReasonScalarMassNotKnown

    @property
    def mass(self) -> 'float':
        '''float: 'Mass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Mass

    @property
    def calculate_acceleration_force_from_mass_matrix(self) -> 'bool':
        '''bool: 'CalculateAccelerationForceFromMassMatrix' is the original name of this property.'''

        return self.wrapped.CalculateAccelerationForceFromMassMatrix

    @calculate_acceleration_force_from_mass_matrix.setter
    def calculate_acceleration_force_from_mass_matrix(self, value: 'bool'):
        self.wrapped.CalculateAccelerationForceFromMassMatrix = bool(value) if value else False

    @property
    def is_using_full_fe_model(self) -> 'bool':
        '''bool: 'IsUsingFullFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsUsingFullFEModel

    @property
    def stiffness_in_fe_coordinate_system_mn_rad(self) -> '_74.NodalMatrix':
        '''NodalMatrix: 'StiffnessInFECoordinateSystemMNRad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_74.NodalMatrix)(self.wrapped.StiffnessInFECoordinateSystemMNRad) if self.wrapped.StiffnessInFECoordinateSystemMNRad is not None else None

    @property
    def mass_matrix_mn_rad_s_kg(self) -> '_74.NodalMatrix':
        '''NodalMatrix: 'MassMatrixMNRadSKg' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_74.NodalMatrix)(self.wrapped.MassMatrixMNRadSKg) if self.wrapped.MassMatrixMNRadSKg is not None else None

    @property
    def centre_of_mass_in_local_coordinate_system(self) -> 'Vector3D':
        '''Vector3D: 'CentreOfMassInLocalCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.CentreOfMassInLocalCoordinateSystem)
        return value

    @property
    def stiffness_matrix(self) -> '_74.NodalMatrix':
        '''NodalMatrix: 'StiffnessMatrix' is the original name of this property.'''

        return constructor.new(_74.NodalMatrix)(self.wrapped.StiffnessMatrix) if self.wrapped.StiffnessMatrix is not None else None

    @stiffness_matrix.setter
    def stiffness_matrix(self, value: '_74.NodalMatrix'):
        value = value.wrapped if value else None
        self.wrapped.StiffnessMatrix = value

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
