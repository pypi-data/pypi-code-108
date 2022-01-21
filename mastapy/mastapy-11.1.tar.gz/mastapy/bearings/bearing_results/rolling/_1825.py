'''_1825.py

TrackTruncationSafetyFactorResults
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TRACK_TRUNCATION_SAFETY_FACTOR_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'TrackTruncationSafetyFactorResults')


__docformat__ = 'restructuredtext en'
__all__ = ('TrackTruncationSafetyFactorResults',)


class TrackTruncationSafetyFactorResults(_0.APIBase):
    '''TrackTruncationSafetyFactorResults

    This is a mastapy class.
    '''

    TYPE = _TRACK_TRUNCATION_SAFETY_FACTOR_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TrackTruncationSafetyFactorResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor(self) -> 'float':
        '''float: 'SafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactor

    @property
    def worst_hertzian_ellipse_major_2b_track_truncation(self) -> 'float':
        '''float: 'WorstHertzianEllipseMajor2bTrackTruncation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorstHertzianEllipseMajor2bTrackTruncation

    @property
    def worst_hertzian_ellipse_major_2b_track_truncation_inner(self) -> 'float':
        '''float: 'WorstHertzianEllipseMajor2bTrackTruncationInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorstHertzianEllipseMajor2bTrackTruncationInner

    @property
    def worst_hertzian_ellipse_major_2b_track_truncation_outer(self) -> 'float':
        '''float: 'WorstHertzianEllipseMajor2bTrackTruncationOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorstHertzianEllipseMajor2bTrackTruncationOuter

    @property
    def smallest_arc_distance_of_raceway_edge_to_hertzian_contact(self) -> 'float':
        '''float: 'SmallestArcDistanceOfRacewayEdgeToHertzianContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SmallestArcDistanceOfRacewayEdgeToHertzianContact

    @property
    def track_truncation_occurring_beyond_permissible_limit(self) -> 'bool':
        '''bool: 'TrackTruncationOccurringBeyondPermissibleLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TrackTruncationOccurringBeyondPermissibleLimit

    @property
    def element_with_worst_track_truncation(self) -> 'str':
        '''str: 'ElementWithWorstTrackTruncation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElementWithWorstTrackTruncation
