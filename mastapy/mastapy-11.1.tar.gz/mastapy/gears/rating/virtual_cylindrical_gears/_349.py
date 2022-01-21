'''_349.py

HypoidVirtualCylindricalGearSetISO10300MethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import _360
from mastapy._internal.python_net import python_net_import

_HYPOID_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'HypoidVirtualCylindricalGearSetISO10300MethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidVirtualCylindricalGearSetISO10300MethodB2',)


class HypoidVirtualCylindricalGearSetISO10300MethodB2(_360.VirtualCylindricalGearSetISO10300MethodB2):
    '''HypoidVirtualCylindricalGearSetISO10300MethodB2

    This is a mastapy class.
    '''

    TYPE = _HYPOID_VIRTUAL_CYLINDRICAL_GEAR_SET_ISO10300_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidVirtualCylindricalGearSetISO10300MethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle_between_direction_of_contact_and_the_pitch_tangent(self) -> 'float':
        '''float: 'AngleBetweenDirectionOfContactAndThePitchTangent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenDirectionOfContactAndThePitchTangent

    @property
    def drive_flank_pressure_angel_in_wheel_root_coordinates(self) -> 'float':
        '''float: 'DriveFlankPressureAngelInWheelRootCoordinates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DriveFlankPressureAngelInWheelRootCoordinates

    @property
    def coast_flank_pressure_angel_in_wheel_root_coordinates(self) -> 'float':
        '''float: 'CoastFlankPressureAngelInWheelRootCoordinates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CoastFlankPressureAngelInWheelRootCoordinates

    @property
    def average_pressure_angle_unbalance(self) -> 'float':
        '''float: 'AveragePressureAngleUnbalance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AveragePressureAngleUnbalance

    @property
    def limit_pressure_angle_in_wheel_root_coordinates(self) -> 'float':
        '''float: 'LimitPressureAngleInWheelRootCoordinates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LimitPressureAngleInWheelRootCoordinates

    @property
    def wheel_mean_slot_width(self) -> 'float':
        '''float: 'WheelMeanSlotWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelMeanSlotWidth

    @property
    def relative_distance_from_blade_edge_to_centreline(self) -> 'float':
        '''float: 'RelativeDistanceFromBladeEdgeToCentreline' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeDistanceFromBladeEdgeToCentreline

    @property
    def wheel_angle_from_centreline_to_pinion_tip_on_drive_side(self) -> 'float':
        '''float: 'WheelAngleFromCentrelineToPinionTipOnDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleFromCentrelineToPinionTipOnDriveSide

    @property
    def deltar_1(self) -> 'float':
        '''float: 'Deltar1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deltar1

    @property
    def h1(self) -> 'float':
        '''float: 'H1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H1

    @property
    def h1o(self) -> 'float':
        '''float: 'H1o' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H1o

    @property
    def wheel_angle_from_centreline_to_tooth_surface_at_pitch_point_on_drive_side(self) -> 'float':
        '''float: 'WheelAngleFromCentrelineToToothSurfaceAtPitchPointOnDriveSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleFromCentrelineToToothSurfaceAtPitchPointOnDriveSide

    @property
    def deltar(self) -> 'float':
        '''float: 'Deltar' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deltar

    @property
    def h(self) -> 'float':
        '''float: 'H' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H

    @property
    def initial_value_for_the_wheel_angle_from_centreline_to_fillet_point_on_drive_flank(self) -> 'float':
        '''float: 'InitialValueForTheWheelAngleFromCentrelineToFilletPointOnDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InitialValueForTheWheelAngleFromCentrelineToFilletPointOnDriveFlank

    @property
    def wheel_angle_from_centreline_to_fillet_point_on_drive_flank(self) -> 'float':
        '''float: 'WheelAngleFromCentrelineToFilletPointOnDriveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngleFromCentrelineToFilletPointOnDriveFlank

    @property
    def deltar_2(self) -> 'float':
        '''float: 'Deltar2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deltar2

    @property
    def h2(self) -> 'float':
        '''float: 'H2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H2

    @property
    def h2o(self) -> 'float':
        '''float: 'H2o' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H2o

    @property
    def length_of_action_from_pinion_tip_to_pitch_circle_in_normal_section(self) -> 'float':
        '''float: 'LengthOfActionFromPinionTipToPitchCircleInNormalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfActionFromPinionTipToPitchCircleInNormalSection

    @property
    def length_of_action_from_wheel_tip_to_pitch_circle_in_normal_section(self) -> 'float':
        '''float: 'LengthOfActionFromWheelTipToPitchCircleInNormalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfActionFromWheelTipToPitchCircleInNormalSection

    @property
    def modified_contact_ratio_for_hypoid_gears(self) -> 'float':
        '''float: 'ModifiedContactRatioForHypoidGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedContactRatioForHypoidGears
