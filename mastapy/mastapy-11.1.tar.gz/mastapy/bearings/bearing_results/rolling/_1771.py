'''_1771.py

LoadedNeedleRollerBearingRow
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1770, _1759
from mastapy._internal.python_net import python_net_import

_LOADED_NEEDLE_ROLLER_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedNeedleRollerBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedNeedleRollerBearingRow',)


class LoadedNeedleRollerBearingRow(_1759.LoadedCylindricalRollerBearingRow):
    '''LoadedNeedleRollerBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_NEEDLE_ROLLER_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedNeedleRollerBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sliding_power_loss(self) -> 'float':
        '''float: 'SlidingPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingPowerLoss

    @property
    def cage_land_sliding_power_loss(self) -> 'float':
        '''float: 'CageLandSlidingPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CageLandSlidingPowerLoss

    @property
    def rolling_power_loss(self) -> 'float':
        '''float: 'RollingPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollingPowerLoss

    @property
    def total_power_loss(self) -> 'float':
        '''float: 'TotalPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalPowerLoss

    @property
    def total_power_loss_traction_coefficient(self) -> 'float':
        '''float: 'TotalPowerLossTractionCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalPowerLossTractionCoefficient

    @property
    def sliding_power_loss_traction_coefficient(self) -> 'float':
        '''float: 'SlidingPowerLossTractionCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingPowerLossTractionCoefficient

    @property
    def rolling_power_loss_traction_coefficient(self) -> 'float':
        '''float: 'RollingPowerLossTractionCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollingPowerLossTractionCoefficient

    @property
    def loaded_bearing(self) -> '_1770.LoadedNeedleRollerBearingResults':
        '''LoadedNeedleRollerBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1770.LoadedNeedleRollerBearingResults)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
