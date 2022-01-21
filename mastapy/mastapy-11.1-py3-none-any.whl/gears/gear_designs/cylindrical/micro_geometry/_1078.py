'''_1078.py

SingleCylindricalGearTriangularEndModification
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SINGLE_CYLINDRICAL_GEAR_TRIANGULAR_END_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'SingleCylindricalGearTriangularEndModification')


__docformat__ = 'restructuredtext en'
__all__ = ('SingleCylindricalGearTriangularEndModification',)


class SingleCylindricalGearTriangularEndModification(_0.APIBase):
    '''SingleCylindricalGearTriangularEndModification

    This is a mastapy class.
    '''

    TYPE = _SINGLE_CYLINDRICAL_GEAR_TRIANGULAR_END_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingleCylindricalGearTriangularEndModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relief(self) -> 'float':
        '''float: 'Relief' is the original name of this property.'''

        return self.wrapped.Relief

    @relief.setter
    def relief(self, value: 'float'):
        self.wrapped.Relief = float(value) if value else 0.0

    @property
    def profile_evaluation_factor(self) -> 'float':
        '''float: 'ProfileEvaluationFactor' is the original name of this property.'''

        return self.wrapped.ProfileEvaluationFactor

    @profile_evaluation_factor.setter
    def profile_evaluation_factor(self, value: 'float'):
        self.wrapped.ProfileEvaluationFactor = float(value) if value else 0.0

    @property
    def profile_evaluation_diameter(self) -> 'float':
        '''float: 'ProfileEvaluationDiameter' is the original name of this property.'''

        return self.wrapped.ProfileEvaluationDiameter

    @profile_evaluation_diameter.setter
    def profile_evaluation_diameter(self, value: 'float'):
        self.wrapped.ProfileEvaluationDiameter = float(value) if value else 0.0

    @property
    def profile_evaluation_radius(self) -> 'float':
        '''float: 'ProfileEvaluationRadius' is the original name of this property.'''

        return self.wrapped.ProfileEvaluationRadius

    @profile_evaluation_radius.setter
    def profile_evaluation_radius(self, value: 'float'):
        self.wrapped.ProfileEvaluationRadius = float(value) if value else 0.0

    @property
    def profile_evaluation_roll_angle(self) -> 'float':
        '''float: 'ProfileEvaluationRollAngle' is the original name of this property.'''

        return self.wrapped.ProfileEvaluationRollAngle

    @profile_evaluation_roll_angle.setter
    def profile_evaluation_roll_angle(self, value: 'float'):
        self.wrapped.ProfileEvaluationRollAngle = float(value) if value else 0.0

    @property
    def profile_evaluation_roll_distance(self) -> 'float':
        '''float: 'ProfileEvaluationRollDistance' is the original name of this property.'''

        return self.wrapped.ProfileEvaluationRollDistance

    @profile_evaluation_roll_distance.setter
    def profile_evaluation_roll_distance(self, value: 'float'):
        self.wrapped.ProfileEvaluationRollDistance = float(value) if value else 0.0

    @property
    def profile_start_factor(self) -> 'float':
        '''float: 'ProfileStartFactor' is the original name of this property.'''

        return self.wrapped.ProfileStartFactor

    @profile_start_factor.setter
    def profile_start_factor(self, value: 'float'):
        self.wrapped.ProfileStartFactor = float(value) if value else 0.0

    @property
    def profile_start_diameter(self) -> 'float':
        '''float: 'ProfileStartDiameter' is the original name of this property.'''

        return self.wrapped.ProfileStartDiameter

    @profile_start_diameter.setter
    def profile_start_diameter(self, value: 'float'):
        self.wrapped.ProfileStartDiameter = float(value) if value else 0.0

    @property
    def profile_start_radius(self) -> 'float':
        '''float: 'ProfileStartRadius' is the original name of this property.'''

        return self.wrapped.ProfileStartRadius

    @profile_start_radius.setter
    def profile_start_radius(self, value: 'float'):
        self.wrapped.ProfileStartRadius = float(value) if value else 0.0

    @property
    def profile_start_roll_angle(self) -> 'float':
        '''float: 'ProfileStartRollAngle' is the original name of this property.'''

        return self.wrapped.ProfileStartRollAngle

    @profile_start_roll_angle.setter
    def profile_start_roll_angle(self, value: 'float'):
        self.wrapped.ProfileStartRollAngle = float(value) if value else 0.0

    @property
    def profile_start_roll_distance(self) -> 'float':
        '''float: 'ProfileStartRollDistance' is the original name of this property.'''

        return self.wrapped.ProfileStartRollDistance

    @profile_start_roll_distance.setter
    def profile_start_roll_distance(self, value: 'float'):
        self.wrapped.ProfileStartRollDistance = float(value) if value else 0.0

    @property
    def face_width_position_factor(self) -> 'float':
        '''float: 'FaceWidthPositionFactor' is the original name of this property.'''

        return self.wrapped.FaceWidthPositionFactor

    @face_width_position_factor.setter
    def face_width_position_factor(self, value: 'float'):
        self.wrapped.FaceWidthPositionFactor = float(value) if value else 0.0

    @property
    def face_width_position(self) -> 'float':
        '''float: 'FaceWidthPosition' is the original name of this property.'''

        return self.wrapped.FaceWidthPosition

    @face_width_position.setter
    def face_width_position(self, value: 'float'):
        self.wrapped.FaceWidthPosition = float(value) if value else 0.0

    @property
    def angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Angle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Angle) if self.wrapped.Angle is not None else None

    @angle.setter
    def angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Angle = value

    @property
    def profile_evaluation(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ProfileEvaluation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ProfileEvaluation) if self.wrapped.ProfileEvaluation is not None else None

    @property
    def profile_start(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ProfileStart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ProfileStart) if self.wrapped.ProfileStart is not None else None

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
