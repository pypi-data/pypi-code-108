'''_1748.py

LoadedBallBearingDutyCycle
'''


from mastapy._internal import constructor
from mastapy.utility.property import _1607
from mastapy.bearings.bearing_results.rolling import _1751
from mastapy.bearings.bearing_results import _1713
from mastapy._internal.python_net import python_net_import

_LOADED_BALL_BEARING_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedBallBearingDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBallBearingDutyCycle',)


class LoadedBallBearingDutyCycle(_1713.LoadedRollingBearingDutyCycle):
    '''LoadedBallBearingDutyCycle

    This is a mastapy class.
    '''

    TYPE = _LOADED_BALL_BEARING_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedBallBearingDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def track_truncation_safety_factor(self) -> 'float':
        '''float: 'TrackTruncationSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TrackTruncationSafetyFactor

    @property
    def track_truncation_inner_summary(self) -> '_1607.DutyCyclePropertySummaryPercentage[_1751.LoadedBallBearingResults]':
        '''DutyCyclePropertySummaryPercentage[LoadedBallBearingResults]: 'TrackTruncationInnerSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1607.DutyCyclePropertySummaryPercentage)[_1751.LoadedBallBearingResults](self.wrapped.TrackTruncationInnerSummary) if self.wrapped.TrackTruncationInnerSummary is not None else None

    @property
    def track_truncation_outer_summary(self) -> '_1607.DutyCyclePropertySummaryPercentage[_1751.LoadedBallBearingResults]':
        '''DutyCyclePropertySummaryPercentage[LoadedBallBearingResults]: 'TrackTruncationOuterSummary' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1607.DutyCyclePropertySummaryPercentage)[_1751.LoadedBallBearingResults](self.wrapped.TrackTruncationOuterSummary) if self.wrapped.TrackTruncationOuterSummary is not None else None
