'''_1802.py

LoadedThreePointContactBallBearingRow
'''


from mastapy.bearings.bearing_results.rolling import _1801, _1752
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_LOADED_THREE_POINT_CONTACT_BALL_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedThreePointContactBallBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedThreePointContactBallBearingRow',)


class LoadedThreePointContactBallBearingRow(_1752.LoadedBallBearingRow):
    '''LoadedThreePointContactBallBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_THREE_POINT_CONTACT_BALL_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedThreePointContactBallBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def loaded_bearing(self) -> '_1801.LoadedThreePointContactBallBearingResults':
        '''LoadedThreePointContactBallBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1801.LoadedThreePointContactBallBearingResults)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
