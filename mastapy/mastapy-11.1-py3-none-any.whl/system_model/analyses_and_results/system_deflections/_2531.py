'''_2531.py

RingPinToDiscContactReporting
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.reporting import _2585
from mastapy.system_model.analyses_and_results.static_loads import _6626
from mastapy.system_model.analyses_and_results.system_deflections import _2501
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RING_PIN_TO_DISC_CONTACT_REPORTING = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'RingPinToDiscContactReporting')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinToDiscContactReporting',)


class RingPinToDiscContactReporting(_0.APIBase):
    '''RingPinToDiscContactReporting

    This is a mastapy class.
    '''

    TYPE = _RING_PIN_TO_DISC_CONTACT_REPORTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinToDiscContactReporting.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pin_number(self) -> 'int':
        '''int: 'PinNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinNumber

    @property
    def maximum_contact_stress(self) -> 'float':
        '''float: 'MaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStress

    @property
    def sliding_velocity(self) -> 'float':
        '''float: 'SlidingVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingVelocity

    @property
    def pressure_velocity(self) -> 'float':
        '''float: 'PressureVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PressureVelocity

    @property
    def contact(self) -> '_2585.SplineFlankContactReporting':
        '''SplineFlankContactReporting: 'Contact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2585.SplineFlankContactReporting)(self.wrapped.Contact) if self.wrapped.Contact is not None else None

    @property
    def information_at_ring_pin_to_disc_contact_point_from_geometry(self) -> '_6626.InformationAtRingPinToDiscContactPointFromGeometry':
        '''InformationAtRingPinToDiscContactPointFromGeometry: 'InformationAtRingPinToDiscContactPointFromGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6626.InformationAtRingPinToDiscContactPointFromGeometry)(self.wrapped.InformationAtRingPinToDiscContactPointFromGeometry) if self.wrapped.InformationAtRingPinToDiscContactPointFromGeometry is not None else None

    @property
    def information_for_contact_points_along_face_width(self) -> 'List[_2501.InformationForContactAtPointAlongFaceWidth]':
        '''List[InformationForContactAtPointAlongFaceWidth]: 'InformationForContactPointsAlongFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InformationForContactPointsAlongFaceWidth, constructor.new(_2501.InformationForContactAtPointAlongFaceWidth))
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
