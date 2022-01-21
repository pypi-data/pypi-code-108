'''_360.py

VirtualCylindricalGearSetISO10300MethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import _358, _357
from mastapy._internal.python_net import python_net_import

_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'VirtualCylindricalGearSetISO10300MethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualCylindricalGearSetISO10300MethodB2',)


class VirtualCylindricalGearSetISO10300MethodB2(_358.VirtualCylindricalGearSet['_357.VirtualCylindricalGearISO10300MethodB2']):
    '''VirtualCylindricalGearSetISO10300MethodB2

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualCylindricalGearSetISO10300MethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relative_length_of_action_in_normal_section(self) -> 'float':
        '''float: 'RelativeLengthOfActionInNormalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeLengthOfActionInNormalSection

    @property
    def modified_contact_ratio(self) -> 'float':
        '''float: 'ModifiedContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedContactRatio

    @property
    def angular_pitch_of_virtual_cylindrical_wheel(self) -> 'float':
        '''float: 'AngularPitchOfVirtualCylindricalWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularPitchOfVirtualCylindricalWheel

    @property
    def contact_shift_factor(self) -> 'float':
        '''float: 'ContactShiftFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactShiftFactor

    @property
    def angle_between_contact_direction_and_tooth_tangent_in_pitch_plane(self) -> 'float':
        '''float: 'AngleBetweenContactDirectionAndToothTangentInPitchPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenContactDirectionAndToothTangentInPitchPlane

    @property
    def angle_between_projection_of_pinion_axis_and_direction_of_contact_in_pitch_plane(self) -> 'float':
        '''float: 'AngleBetweenProjectionOfPinionAxisAndDirectionOfContactInPitchPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenProjectionOfPinionAxisAndDirectionOfContactInPitchPlane

    @property
    def angle_of_contact_line_relative_to_root_cone(self) -> 'float':
        '''float: 'AngleOfContactLineRelativeToRootCone' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleOfContactLineRelativeToRootCone

    @property
    def mean_base_spiral_angle(self) -> 'float':
        '''float: 'MeanBaseSpiralAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanBaseSpiralAngle

    @property
    def relative_mean_normal_base_pitch(self) -> 'float':
        '''float: 'RelativeMeanNormalBasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanNormalBasePitch

    @property
    def angle_between_projection_of_wheel_axis_and_direction_of_contact_in_pitch_plane(self) -> 'float':
        '''float: 'AngleBetweenProjectionOfWheelAxisAndDirectionOfContactInPitchPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenProjectionOfWheelAxisAndDirectionOfContactInPitchPlane

    @property
    def relative_base_face_width(self) -> 'float':
        '''float: 'RelativeBaseFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeBaseFaceWidth

    @property
    def relative_face_width(self) -> 'float':
        '''float: 'RelativeFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeFaceWidth

    @property
    def relative_centre_distance(self) -> 'float':
        '''float: 'RelativeCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeCentreDistance
