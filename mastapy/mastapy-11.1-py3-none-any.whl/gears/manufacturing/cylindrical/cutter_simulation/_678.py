'''_678.py

ShavingSimulationCalculator
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.cutter_simulation import _663
from mastapy._internal.python_net import python_net_import

_SHAVING_SIMULATION_CALCULATOR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'ShavingSimulationCalculator')


__docformat__ = 'restructuredtext en'
__all__ = ('ShavingSimulationCalculator',)


class ShavingSimulationCalculator(_663.CutterSimulationCalc):
    '''ShavingSimulationCalculator

    This is a mastapy class.
    '''

    TYPE = _SHAVING_SIMULATION_CALCULATOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShavingSimulationCalculator.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cross_angle(self) -> 'float':
        '''float: 'CrossAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrossAngle

    @property
    def shaving_centre_distance(self) -> 'float':
        '''float: 'ShavingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShavingCentreDistance

    @property
    def gear_normal_shaving_pitch_pressure_angle(self) -> 'float':
        '''float: 'GearNormalShavingPitchPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearNormalShavingPitchPressureAngle

    @property
    def gear_transverse_shaving_pitch_pressure_angle(self) -> 'float':
        '''float: 'GearTransverseShavingPitchPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearTransverseShavingPitchPressureAngle

    @property
    def shaver_transverse_shaving_pitch_pressure_angle(self) -> 'float':
        '''float: 'ShaverTransverseShavingPitchPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverTransverseShavingPitchPressureAngle

    @property
    def theoretical_shaving_contact_ratio(self) -> 'float':
        '''float: 'TheoreticalShavingContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TheoreticalShavingContactRatio

    @property
    def minimum_centre_distance(self) -> 'float':
        '''float: 'MinimumCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumCentreDistance

    @property
    def least_centre_distance_cross_angle(self) -> 'float':
        '''float: 'LeastCentreDistanceCrossAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeastCentreDistanceCrossAngle
