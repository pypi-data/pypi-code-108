'''_1751.py

LoadedBallBearingResults
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.bearings.bearing_results.rolling import _1725, _1825, _1782
from mastapy._internal.python_net import python_net_import

_LOADED_BALL_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedBallBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBallBearingResults',)


class LoadedBallBearingResults(_1782.LoadedRollingBearingResults):
    '''LoadedBallBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_BALL_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedBallBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_element_contact_angles_for_angular_velocities(self) -> 'bool':
        '''bool: 'UseElementContactAnglesForAngularVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UseElementContactAnglesForAngularVelocities

    @property
    def friction_model_for_gyroscopic_moment(self) -> '_1725.FrictionModelForGyroscopicMoment':
        '''FrictionModelForGyroscopicMoment: 'FrictionModelForGyroscopicMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.FrictionModelForGyroscopicMoment)
        return constructor.new(_1725.FrictionModelForGyroscopicMoment)(value) if value is not None else None

    @property
    def track_truncation(self) -> '_1825.TrackTruncationSafetyFactorResults':
        '''TrackTruncationSafetyFactorResults: 'TrackTruncation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1825.TrackTruncationSafetyFactorResults)(self.wrapped.TrackTruncation) if self.wrapped.TrackTruncation is not None else None
