'''_992.py

CylindricalMeshedGear
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _993
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MESHED_GEAR = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalMeshedGear')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshedGear',)


class CylindricalMeshedGear(_0.APIBase):
    '''CylindricalMeshedGear

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESHED_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshedGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def working_pitch_diameter(self) -> 'float':
        '''float: 'WorkingPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingPitchDiameter

    @property
    def face_width_to_working_pitch_diameter_ratio(self) -> 'float':
        '''float: 'FaceWidthToWorkingPitchDiameterRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthToWorkingPitchDiameterRatio

    @property
    def effective_face_width_to_reference_diameter_ratio(self) -> 'float':
        '''float: 'EffectiveFaceWidthToReferenceDiameterRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidthToReferenceDiameterRatio

    @property
    def tip_clearance_factor(self) -> 'float':
        '''float: 'TipClearanceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipClearanceFactor

    @property
    def tip_clearance_at_tight_mesh_maximum_metal(self) -> 'float':
        '''float: 'TipClearanceAtTightMeshMaximumMetal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipClearanceAtTightMeshMaximumMetal

    @property
    def tip_clearance_at_tight_mesh_minimum_metal(self) -> 'float':
        '''float: 'TipClearanceAtTightMeshMinimumMetal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipClearanceAtTightMeshMinimumMetal

    @property
    def tip_clearance(self) -> 'float':
        '''float: 'TipClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipClearance

    @property
    def left_flank(self) -> '_993.CylindricalMeshedGearFlank':
        '''CylindricalMeshedGearFlank: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_993.CylindricalMeshedGearFlank)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def right_flank(self) -> '_993.CylindricalMeshedGearFlank':
        '''CylindricalMeshedGearFlank: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_993.CylindricalMeshedGearFlank)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def flanks(self) -> 'List[_993.CylindricalMeshedGearFlank]':
        '''List[CylindricalMeshedGearFlank]: 'Flanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Flanks, constructor.new(_993.CylindricalMeshedGearFlank))
        return value

    @property
    def both_flanks(self) -> '_993.CylindricalMeshedGearFlank':
        '''CylindricalMeshedGearFlank: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_993.CylindricalMeshedGearFlank)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None

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
