'''_1055.py

CylindricalGearProfileModification
'''


from mastapy._internal import constructor
from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy.gears.micro_geometry import _542
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_PROFILE_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearProfileModification')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearProfileModification',)


class CylindricalGearProfileModification(_542.ProfileModification):
    '''CylindricalGearProfileModification

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_PROFILE_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearProfileModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pressure_angle_modification(self) -> 'float':
        '''float: 'PressureAngleModification' is the original name of this property.'''

        return self.wrapped.PressureAngleModification

    @pressure_angle_modification.setter
    def pressure_angle_modification(self, value: 'float'):
        self.wrapped.PressureAngleModification = float(value) if value else 0.0

    @property
    def start_of_linear_root_relief_roll_distance(self) -> 'float':
        '''float: 'StartOfLinearRootReliefRollDistance' is the original name of this property.'''

        return self.wrapped.StartOfLinearRootReliefRollDistance

    @start_of_linear_root_relief_roll_distance.setter
    def start_of_linear_root_relief_roll_distance(self, value: 'float'):
        self.wrapped.StartOfLinearRootReliefRollDistance = float(value) if value else 0.0

    @property
    def start_of_parabolic_root_relief_roll_distance(self) -> 'float':
        '''float: 'StartOfParabolicRootReliefRollDistance' is the original name of this property.'''

        return self.wrapped.StartOfParabolicRootReliefRollDistance

    @start_of_parabolic_root_relief_roll_distance.setter
    def start_of_parabolic_root_relief_roll_distance(self, value: 'float'):
        self.wrapped.StartOfParabolicRootReliefRollDistance = float(value) if value else 0.0

    @property
    def start_of_linear_tip_relief_roll_distance(self) -> 'float':
        '''float: 'StartOfLinearTipReliefRollDistance' is the original name of this property.'''

        return self.wrapped.StartOfLinearTipReliefRollDistance

    @start_of_linear_tip_relief_roll_distance.setter
    def start_of_linear_tip_relief_roll_distance(self, value: 'float'):
        self.wrapped.StartOfLinearTipReliefRollDistance = float(value) if value else 0.0

    @property
    def barrelling_peak_point_roll_distance(self) -> 'float':
        '''float: 'BarrellingPeakPointRollDistance' is the original name of this property.'''

        return self.wrapped.BarrellingPeakPointRollDistance

    @barrelling_peak_point_roll_distance.setter
    def barrelling_peak_point_roll_distance(self, value: 'float'):
        self.wrapped.BarrellingPeakPointRollDistance = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_roll_distance(self) -> 'float':
        '''float: 'EvaluationLowerLimitRollDistance' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitRollDistance

    @evaluation_lower_limit_roll_distance.setter
    def evaluation_lower_limit_roll_distance(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitRollDistance = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_roll_distance(self) -> 'float':
        '''float: 'EvaluationUpperLimitRollDistance' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitRollDistance

    @evaluation_upper_limit_roll_distance.setter
    def evaluation_upper_limit_roll_distance(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitRollDistance = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_roll_distance_for_zero_tip_relief(self) -> 'float':
        '''float: 'EvaluationUpperLimitRollDistanceForZeroTipRelief' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitRollDistanceForZeroTipRelief

    @evaluation_upper_limit_roll_distance_for_zero_tip_relief.setter
    def evaluation_upper_limit_roll_distance_for_zero_tip_relief(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitRollDistanceForZeroTipRelief = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_roll_distance_for_zero_root_relief(self) -> 'float':
        '''float: 'EvaluationLowerLimitRollDistanceForZeroRootRelief' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitRollDistanceForZeroRootRelief

    @evaluation_lower_limit_roll_distance_for_zero_root_relief.setter
    def evaluation_lower_limit_roll_distance_for_zero_root_relief(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitRollDistanceForZeroRootRelief = float(value) if value else 0.0

    @property
    def start_of_parabolic_tip_relief_roll_distance(self) -> 'float':
        '''float: 'StartOfParabolicTipReliefRollDistance' is the original name of this property.'''

        return self.wrapped.StartOfParabolicTipReliefRollDistance

    @start_of_parabolic_tip_relief_roll_distance.setter
    def start_of_parabolic_tip_relief_roll_distance(self, value: 'float'):
        self.wrapped.StartOfParabolicTipReliefRollDistance = float(value) if value else 0.0

    @property
    def evaluation_of_linear_tip_relief_roll_distance(self) -> 'float':
        '''float: 'EvaluationOfLinearTipReliefRollDistance' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearTipReliefRollDistance

    @evaluation_of_linear_tip_relief_roll_distance.setter
    def evaluation_of_linear_tip_relief_roll_distance(self, value: 'float'):
        self.wrapped.EvaluationOfLinearTipReliefRollDistance = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_tip_relief_roll_distance(self) -> 'float':
        '''float: 'EvaluationOfParabolicTipReliefRollDistance' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicTipReliefRollDistance

    @evaluation_of_parabolic_tip_relief_roll_distance.setter
    def evaluation_of_parabolic_tip_relief_roll_distance(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicTipReliefRollDistance = float(value) if value else 0.0

    @property
    def evaluation_of_linear_root_relief_roll_distance(self) -> 'float':
        '''float: 'EvaluationOfLinearRootReliefRollDistance' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearRootReliefRollDistance

    @evaluation_of_linear_root_relief_roll_distance.setter
    def evaluation_of_linear_root_relief_roll_distance(self, value: 'float'):
        self.wrapped.EvaluationOfLinearRootReliefRollDistance = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_root_relief_roll_distance(self) -> 'float':
        '''float: 'EvaluationOfParabolicRootReliefRollDistance' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicRootReliefRollDistance

    @evaluation_of_parabolic_root_relief_roll_distance.setter
    def evaluation_of_parabolic_root_relief_roll_distance(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicRootReliefRollDistance = float(value) if value else 0.0

    @property
    def start_of_linear_root_relief_roll_angle(self) -> 'float':
        '''float: 'StartOfLinearRootReliefRollAngle' is the original name of this property.'''

        return self.wrapped.StartOfLinearRootReliefRollAngle

    @start_of_linear_root_relief_roll_angle.setter
    def start_of_linear_root_relief_roll_angle(self, value: 'float'):
        self.wrapped.StartOfLinearRootReliefRollAngle = float(value) if value else 0.0

    @property
    def start_of_parabolic_root_relief_roll_angle(self) -> 'float':
        '''float: 'StartOfParabolicRootReliefRollAngle' is the original name of this property.'''

        return self.wrapped.StartOfParabolicRootReliefRollAngle

    @start_of_parabolic_root_relief_roll_angle.setter
    def start_of_parabolic_root_relief_roll_angle(self, value: 'float'):
        self.wrapped.StartOfParabolicRootReliefRollAngle = float(value) if value else 0.0

    @property
    def start_of_linear_tip_relief_roll_angle(self) -> 'float':
        '''float: 'StartOfLinearTipReliefRollAngle' is the original name of this property.'''

        return self.wrapped.StartOfLinearTipReliefRollAngle

    @start_of_linear_tip_relief_roll_angle.setter
    def start_of_linear_tip_relief_roll_angle(self, value: 'float'):
        self.wrapped.StartOfLinearTipReliefRollAngle = float(value) if value else 0.0

    @property
    def barrelling_peak_point_roll_angle(self) -> 'float':
        '''float: 'BarrellingPeakPointRollAngle' is the original name of this property.'''

        return self.wrapped.BarrellingPeakPointRollAngle

    @barrelling_peak_point_roll_angle.setter
    def barrelling_peak_point_roll_angle(self, value: 'float'):
        self.wrapped.BarrellingPeakPointRollAngle = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_roll_angle(self) -> 'float':
        '''float: 'EvaluationLowerLimitRollAngle' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitRollAngle

    @evaluation_lower_limit_roll_angle.setter
    def evaluation_lower_limit_roll_angle(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitRollAngle = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_roll_angle(self) -> 'float':
        '''float: 'EvaluationUpperLimitRollAngle' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitRollAngle

    @evaluation_upper_limit_roll_angle.setter
    def evaluation_upper_limit_roll_angle(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitRollAngle = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_roll_angle_for_zero_tip_relief(self) -> 'float':
        '''float: 'EvaluationUpperLimitRollAngleForZeroTipRelief' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitRollAngleForZeroTipRelief

    @evaluation_upper_limit_roll_angle_for_zero_tip_relief.setter
    def evaluation_upper_limit_roll_angle_for_zero_tip_relief(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitRollAngleForZeroTipRelief = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_roll_angle_for_zero_root_relief(self) -> 'float':
        '''float: 'EvaluationLowerLimitRollAngleForZeroRootRelief' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitRollAngleForZeroRootRelief

    @evaluation_lower_limit_roll_angle_for_zero_root_relief.setter
    def evaluation_lower_limit_roll_angle_for_zero_root_relief(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitRollAngleForZeroRootRelief = float(value) if value else 0.0

    @property
    def start_of_parabolic_tip_relief_roll_angle(self) -> 'float':
        '''float: 'StartOfParabolicTipReliefRollAngle' is the original name of this property.'''

        return self.wrapped.StartOfParabolicTipReliefRollAngle

    @start_of_parabolic_tip_relief_roll_angle.setter
    def start_of_parabolic_tip_relief_roll_angle(self, value: 'float'):
        self.wrapped.StartOfParabolicTipReliefRollAngle = float(value) if value else 0.0

    @property
    def evaluation_of_linear_tip_relief_roll_angle(self) -> 'float':
        '''float: 'EvaluationOfLinearTipReliefRollAngle' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearTipReliefRollAngle

    @evaluation_of_linear_tip_relief_roll_angle.setter
    def evaluation_of_linear_tip_relief_roll_angle(self, value: 'float'):
        self.wrapped.EvaluationOfLinearTipReliefRollAngle = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_tip_relief_roll_angle(self) -> 'float':
        '''float: 'EvaluationOfParabolicTipReliefRollAngle' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicTipReliefRollAngle

    @evaluation_of_parabolic_tip_relief_roll_angle.setter
    def evaluation_of_parabolic_tip_relief_roll_angle(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicTipReliefRollAngle = float(value) if value else 0.0

    @property
    def evaluation_of_linear_root_relief_roll_angle(self) -> 'float':
        '''float: 'EvaluationOfLinearRootReliefRollAngle' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearRootReliefRollAngle

    @evaluation_of_linear_root_relief_roll_angle.setter
    def evaluation_of_linear_root_relief_roll_angle(self, value: 'float'):
        self.wrapped.EvaluationOfLinearRootReliefRollAngle = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_root_relief_roll_angle(self) -> 'float':
        '''float: 'EvaluationOfParabolicRootReliefRollAngle' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicRootReliefRollAngle

    @evaluation_of_parabolic_root_relief_roll_angle.setter
    def evaluation_of_parabolic_root_relief_roll_angle(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicRootReliefRollAngle = float(value) if value else 0.0

    @property
    def start_of_linear_root_relief_diameter(self) -> 'float':
        '''float: 'StartOfLinearRootReliefDiameter' is the original name of this property.'''

        return self.wrapped.StartOfLinearRootReliefDiameter

    @start_of_linear_root_relief_diameter.setter
    def start_of_linear_root_relief_diameter(self, value: 'float'):
        self.wrapped.StartOfLinearRootReliefDiameter = float(value) if value else 0.0

    @property
    def start_of_parabolic_root_relief_diameter(self) -> 'float':
        '''float: 'StartOfParabolicRootReliefDiameter' is the original name of this property.'''

        return self.wrapped.StartOfParabolicRootReliefDiameter

    @start_of_parabolic_root_relief_diameter.setter
    def start_of_parabolic_root_relief_diameter(self, value: 'float'):
        self.wrapped.StartOfParabolicRootReliefDiameter = float(value) if value else 0.0

    @property
    def start_of_linear_tip_relief_diameter(self) -> 'float':
        '''float: 'StartOfLinearTipReliefDiameter' is the original name of this property.'''

        return self.wrapped.StartOfLinearTipReliefDiameter

    @start_of_linear_tip_relief_diameter.setter
    def start_of_linear_tip_relief_diameter(self, value: 'float'):
        self.wrapped.StartOfLinearTipReliefDiameter = float(value) if value else 0.0

    @property
    def barrelling_peak_point_diameter(self) -> 'float':
        '''float: 'BarrellingPeakPointDiameter' is the original name of this property.'''

        return self.wrapped.BarrellingPeakPointDiameter

    @barrelling_peak_point_diameter.setter
    def barrelling_peak_point_diameter(self, value: 'float'):
        self.wrapped.BarrellingPeakPointDiameter = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_diameter(self) -> 'float':
        '''float: 'EvaluationLowerLimitDiameter' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitDiameter

    @evaluation_lower_limit_diameter.setter
    def evaluation_lower_limit_diameter(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitDiameter = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_diameter(self) -> 'float':
        '''float: 'EvaluationUpperLimitDiameter' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitDiameter

    @evaluation_upper_limit_diameter.setter
    def evaluation_upper_limit_diameter(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitDiameter = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_diameter_for_zero_tip_relief(self) -> 'float':
        '''float: 'EvaluationUpperLimitDiameterForZeroTipRelief' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitDiameterForZeroTipRelief

    @evaluation_upper_limit_diameter_for_zero_tip_relief.setter
    def evaluation_upper_limit_diameter_for_zero_tip_relief(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitDiameterForZeroTipRelief = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_diameter_for_zero_root_relief(self) -> 'float':
        '''float: 'EvaluationLowerLimitDiameterForZeroRootRelief' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitDiameterForZeroRootRelief

    @evaluation_lower_limit_diameter_for_zero_root_relief.setter
    def evaluation_lower_limit_diameter_for_zero_root_relief(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitDiameterForZeroRootRelief = float(value) if value else 0.0

    @property
    def start_of_parabolic_tip_relief_diameter(self) -> 'float':
        '''float: 'StartOfParabolicTipReliefDiameter' is the original name of this property.'''

        return self.wrapped.StartOfParabolicTipReliefDiameter

    @start_of_parabolic_tip_relief_diameter.setter
    def start_of_parabolic_tip_relief_diameter(self, value: 'float'):
        self.wrapped.StartOfParabolicTipReliefDiameter = float(value) if value else 0.0

    @property
    def evaluation_of_linear_tip_relief_diameter(self) -> 'float':
        '''float: 'EvaluationOfLinearTipReliefDiameter' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearTipReliefDiameter

    @evaluation_of_linear_tip_relief_diameter.setter
    def evaluation_of_linear_tip_relief_diameter(self, value: 'float'):
        self.wrapped.EvaluationOfLinearTipReliefDiameter = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_tip_relief_diameter(self) -> 'float':
        '''float: 'EvaluationOfParabolicTipReliefDiameter' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicTipReliefDiameter

    @evaluation_of_parabolic_tip_relief_diameter.setter
    def evaluation_of_parabolic_tip_relief_diameter(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicTipReliefDiameter = float(value) if value else 0.0

    @property
    def evaluation_of_linear_root_relief_diameter(self) -> 'float':
        '''float: 'EvaluationOfLinearRootReliefDiameter' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearRootReliefDiameter

    @evaluation_of_linear_root_relief_diameter.setter
    def evaluation_of_linear_root_relief_diameter(self, value: 'float'):
        self.wrapped.EvaluationOfLinearRootReliefDiameter = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_root_relief_diameter(self) -> 'float':
        '''float: 'EvaluationOfParabolicRootReliefDiameter' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicRootReliefDiameter

    @evaluation_of_parabolic_root_relief_diameter.setter
    def evaluation_of_parabolic_root_relief_diameter(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicRootReliefDiameter = float(value) if value else 0.0

    @property
    def start_of_linear_root_relief_radius(self) -> 'float':
        '''float: 'StartOfLinearRootReliefRadius' is the original name of this property.'''

        return self.wrapped.StartOfLinearRootReliefRadius

    @start_of_linear_root_relief_radius.setter
    def start_of_linear_root_relief_radius(self, value: 'float'):
        self.wrapped.StartOfLinearRootReliefRadius = float(value) if value else 0.0

    @property
    def start_of_parabolic_root_relief_radius(self) -> 'float':
        '''float: 'StartOfParabolicRootReliefRadius' is the original name of this property.'''

        return self.wrapped.StartOfParabolicRootReliefRadius

    @start_of_parabolic_root_relief_radius.setter
    def start_of_parabolic_root_relief_radius(self, value: 'float'):
        self.wrapped.StartOfParabolicRootReliefRadius = float(value) if value else 0.0

    @property
    def start_of_linear_tip_relief_radius(self) -> 'float':
        '''float: 'StartOfLinearTipReliefRadius' is the original name of this property.'''

        return self.wrapped.StartOfLinearTipReliefRadius

    @start_of_linear_tip_relief_radius.setter
    def start_of_linear_tip_relief_radius(self, value: 'float'):
        self.wrapped.StartOfLinearTipReliefRadius = float(value) if value else 0.0

    @property
    def barrelling_peak_point_radius(self) -> 'float':
        '''float: 'BarrellingPeakPointRadius' is the original name of this property.'''

        return self.wrapped.BarrellingPeakPointRadius

    @barrelling_peak_point_radius.setter
    def barrelling_peak_point_radius(self, value: 'float'):
        self.wrapped.BarrellingPeakPointRadius = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_radius(self) -> 'float':
        '''float: 'EvaluationLowerLimitRadius' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitRadius

    @evaluation_lower_limit_radius.setter
    def evaluation_lower_limit_radius(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitRadius = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_radius(self) -> 'float':
        '''float: 'EvaluationUpperLimitRadius' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitRadius

    @evaluation_upper_limit_radius.setter
    def evaluation_upper_limit_radius(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitRadius = float(value) if value else 0.0

    @property
    def evaluation_upper_limit_radius_for_zero_tip_relief(self) -> 'float':
        '''float: 'EvaluationUpperLimitRadiusForZeroTipRelief' is the original name of this property.'''

        return self.wrapped.EvaluationUpperLimitRadiusForZeroTipRelief

    @evaluation_upper_limit_radius_for_zero_tip_relief.setter
    def evaluation_upper_limit_radius_for_zero_tip_relief(self, value: 'float'):
        self.wrapped.EvaluationUpperLimitRadiusForZeroTipRelief = float(value) if value else 0.0

    @property
    def evaluation_lower_limit_radius_for_zero_root_relief(self) -> 'float':
        '''float: 'EvaluationLowerLimitRadiusForZeroRootRelief' is the original name of this property.'''

        return self.wrapped.EvaluationLowerLimitRadiusForZeroRootRelief

    @evaluation_lower_limit_radius_for_zero_root_relief.setter
    def evaluation_lower_limit_radius_for_zero_root_relief(self, value: 'float'):
        self.wrapped.EvaluationLowerLimitRadiusForZeroRootRelief = float(value) if value else 0.0

    @property
    def start_of_parabolic_tip_relief_radius(self) -> 'float':
        '''float: 'StartOfParabolicTipReliefRadius' is the original name of this property.'''

        return self.wrapped.StartOfParabolicTipReliefRadius

    @start_of_parabolic_tip_relief_radius.setter
    def start_of_parabolic_tip_relief_radius(self, value: 'float'):
        self.wrapped.StartOfParabolicTipReliefRadius = float(value) if value else 0.0

    @property
    def evaluation_of_linear_tip_relief_radius(self) -> 'float':
        '''float: 'EvaluationOfLinearTipReliefRadius' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearTipReliefRadius

    @evaluation_of_linear_tip_relief_radius.setter
    def evaluation_of_linear_tip_relief_radius(self, value: 'float'):
        self.wrapped.EvaluationOfLinearTipReliefRadius = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_tip_relief_radius(self) -> 'float':
        '''float: 'EvaluationOfParabolicTipReliefRadius' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicTipReliefRadius

    @evaluation_of_parabolic_tip_relief_radius.setter
    def evaluation_of_parabolic_tip_relief_radius(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicTipReliefRadius = float(value) if value else 0.0

    @property
    def evaluation_of_linear_root_relief_radius(self) -> 'float':
        '''float: 'EvaluationOfLinearRootReliefRadius' is the original name of this property.'''

        return self.wrapped.EvaluationOfLinearRootReliefRadius

    @evaluation_of_linear_root_relief_radius.setter
    def evaluation_of_linear_root_relief_radius(self, value: 'float'):
        self.wrapped.EvaluationOfLinearRootReliefRadius = float(value) if value else 0.0

    @property
    def evaluation_of_parabolic_root_relief_radius(self) -> 'float':
        '''float: 'EvaluationOfParabolicRootReliefRadius' is the original name of this property.'''

        return self.wrapped.EvaluationOfParabolicRootReliefRadius

    @evaluation_of_parabolic_root_relief_radius.setter
    def evaluation_of_parabolic_root_relief_radius(self, value: 'float'):
        self.wrapped.EvaluationOfParabolicRootReliefRadius = float(value) if value else 0.0

    @property
    def profile_modification_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'ProfileModificationChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.ProfileModificationChart.__class__.__mro__:
            raise CastException('Failed to cast profile_modification_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.ProfileModificationChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ProfileModificationChart.__class__)(self.wrapped.ProfileModificationChart) if self.wrapped.ProfileModificationChart is not None else None

    @property
    def linear_relief_ldp(self) -> 'float':
        '''float: 'LinearReliefLDP' is the original name of this property.'''

        return self.wrapped.LinearReliefLDP

    @linear_relief_ldp.setter
    def linear_relief_ldp(self, value: 'float'):
        self.wrapped.LinearReliefLDP = float(value) if value else 0.0

    @property
    def linear_relief_isoagmadin(self) -> 'float':
        '''float: 'LinearReliefISOAGMADIN' is the original name of this property.'''

        return self.wrapped.LinearReliefISOAGMADIN

    @linear_relief_isoagmadin.setter
    def linear_relief_isoagmadin(self, value: 'float'):
        self.wrapped.LinearReliefISOAGMADIN = float(value) if value else 0.0

    @property
    def linear_relief_vdi(self) -> 'float':
        '''float: 'LinearReliefVDI' is the original name of this property.'''

        return self.wrapped.LinearReliefVDI

    @linear_relief_vdi.setter
    def linear_relief_vdi(self, value: 'float'):
        self.wrapped.LinearReliefVDI = float(value) if value else 0.0

    @property
    def linear_root_relief_start(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LinearRootReliefStart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LinearRootReliefStart) if self.wrapped.LinearRootReliefStart is not None else None

    @property
    def parabolic_root_relief_start(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ParabolicRootReliefStart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ParabolicRootReliefStart) if self.wrapped.ParabolicRootReliefStart is not None else None

    @property
    def linear_tip_relief_start(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LinearTipReliefStart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LinearTipReliefStart) if self.wrapped.LinearTipReliefStart is not None else None

    @property
    def parabolic_tip_relief_start(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ParabolicTipReliefStart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ParabolicTipReliefStart) if self.wrapped.ParabolicTipReliefStart is not None else None

    @property
    def barrelling_peak_point(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'BarrellingPeakPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.BarrellingPeakPoint) if self.wrapped.BarrellingPeakPoint is not None else None

    @property
    def evaluation_lower_limit(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'EvaluationLowerLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.EvaluationLowerLimit) if self.wrapped.EvaluationLowerLimit is not None else None

    @property
    def evaluation_upper_limit(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'EvaluationUpperLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.EvaluationUpperLimit) if self.wrapped.EvaluationUpperLimit is not None else None

    @property
    def evaluation_upper_limit_for_zero_tip_relief(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'EvaluationUpperLimitForZeroTipRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.EvaluationUpperLimitForZeroTipRelief) if self.wrapped.EvaluationUpperLimitForZeroTipRelief is not None else None

    @property
    def evaluation_lower_limit_for_zero_root_relief(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'EvaluationLowerLimitForZeroRootRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.EvaluationLowerLimitForZeroRootRelief) if self.wrapped.EvaluationLowerLimitForZeroRootRelief is not None else None

    @property
    def linear_tip_relief_evaluation(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LinearTipReliefEvaluation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LinearTipReliefEvaluation) if self.wrapped.LinearTipReliefEvaluation is not None else None

    @property
    def parabolic_tip_relief_evaluation(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ParabolicTipReliefEvaluation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ParabolicTipReliefEvaluation) if self.wrapped.ParabolicTipReliefEvaluation is not None else None

    @property
    def linear_root_relief_evaluation(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LinearRootReliefEvaluation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LinearRootReliefEvaluation) if self.wrapped.LinearRootReliefEvaluation is not None else None

    @property
    def parabolic_root_relief_evaluation(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ParabolicRootReliefEvaluation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ParabolicRootReliefEvaluation) if self.wrapped.ParabolicRootReliefEvaluation is not None else None

    def relief_of(self, roll_distance: 'float') -> 'float':
        ''' 'ReliefOf' is the original name of this method.

        Args:
            roll_distance (float)

        Returns:
            float
        '''

        roll_distance = float(roll_distance)
        method_result = self.wrapped.ReliefOf(roll_distance if roll_distance else 0.0)
        return method_result
