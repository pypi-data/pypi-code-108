'''_364.py

StraightBevelDiffMeshedGearRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.conical import _505
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_MESHED_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.StraightBevelDiff', 'StraightBevelDiffMeshedGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffMeshedGearRating',)


class StraightBevelDiffMeshedGearRating(_505.ConicalMeshedGearRating):
    '''StraightBevelDiffMeshedGearRating

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_MESHED_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffMeshedGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def peak_torque(self) -> 'float':
        '''float: 'PeakTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeakTorque

    @property
    def performance_torque(self) -> 'float':
        '''float: 'PerformanceTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PerformanceTorque

    @property
    def allowable_bending_stress_for_performance_torque(self) -> 'float':
        '''float: 'AllowableBendingStressForPerformanceTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBendingStressForPerformanceTorque

    @property
    def allowable_bending_stress_for_peak_torque(self) -> 'float':
        '''float: 'AllowableBendingStressForPeakTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBendingStressForPeakTorque

    @property
    def safety_factor_for_performance_torque(self) -> 'float':
        '''float: 'SafetyFactorForPerformanceTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForPerformanceTorque

    @property
    def safety_factor_for_peak_torque(self) -> 'float':
        '''float: 'SafetyFactorForPeakTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForPeakTorque

    @property
    def total_transmitted_peak_torque(self) -> 'float':
        '''float: 'TotalTransmittedPeakTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalTransmittedPeakTorque

    @property
    def calculated_bending_stress_for_peak_torque(self) -> 'float':
        '''float: 'CalculatedBendingStressForPeakTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedBendingStressForPeakTorque

    @property
    def total_torque_transmitted(self) -> 'float':
        '''float: 'TotalTorqueTransmitted' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalTorqueTransmitted

    @property
    def calculated_bending_stress_for_performance_torque(self) -> 'float':
        '''float: 'CalculatedBendingStressForPerformanceTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedBendingStressForPerformanceTorque

    @property
    def strength_factor(self) -> 'float':
        '''float: 'StrengthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthFactor

    @property
    def rating_result(self) -> 'str':
        '''str: 'RatingResult' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingResult
