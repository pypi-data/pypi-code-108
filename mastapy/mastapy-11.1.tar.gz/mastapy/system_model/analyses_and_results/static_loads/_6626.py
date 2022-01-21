'''_6626.py

InformationAtRingPinToDiscContactPointFromGeometry
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INFORMATION_AT_RING_PIN_TO_DISC_CONTACT_POINT_FROM_GEOMETRY = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'InformationAtRingPinToDiscContactPointFromGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('InformationAtRingPinToDiscContactPointFromGeometry',)


class InformationAtRingPinToDiscContactPointFromGeometry(_0.APIBase):
    '''InformationAtRingPinToDiscContactPointFromGeometry

    This is a mastapy class.
    '''

    TYPE = _INFORMATION_AT_RING_PIN_TO_DISC_CONTACT_POINT_FROM_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InformationAtRingPinToDiscContactPointFromGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pin_index(self) -> 'int':
        '''int: 'PinIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinIndex

    @property
    def clearance_due_to_disc_profile(self) -> 'float':
        '''float: 'ClearanceDueToDiscProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClearanceDueToDiscProfile

    @property
    def disc_radius_of_curvature(self) -> 'float':
        '''float: 'DiscRadiusOfCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DiscRadiusOfCurvature

    @property
    def ring_pin_radius_of_curvature(self) -> 'float':
        '''float: 'RingPinRadiusOfCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RingPinRadiusOfCurvature

    @property
    def combined_radius_of_curvature(self) -> 'float':
        '''float: 'CombinedRadiusOfCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedRadiusOfCurvature

    @property
    def combined_curvature(self) -> 'float':
        '''float: 'CombinedCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedCurvature

    @property
    def clearance_due_to_ring_pin_manufacturing_errors(self) -> 'float':
        '''float: 'ClearanceDueToRingPinManufacturingErrors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClearanceDueToRingPinManufacturingErrors

    @property
    def total_clearance(self) -> 'float':
        '''float: 'TotalClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalClearance

    @property
    def normalised_arc_length_along_half_lobe_to_contact(self) -> 'float':
        '''float: 'NormalisedArcLengthAlongHalfLobeToContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalisedArcLengthAlongHalfLobeToContact
