'''_1733.py

LoadedAngularContactBallBearingRow
'''


from mastapy.bearings.bearing_results.rolling import _1732, _1735, _1752
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_LOADED_ANGULAR_CONTACT_BALL_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAngularContactBallBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAngularContactBallBearingRow',)


class LoadedAngularContactBallBearingRow(_1752.LoadedBallBearingRow):
    '''LoadedAngularContactBallBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_ANGULAR_CONTACT_BALL_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAngularContactBallBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def loaded_bearing(self) -> '_1732.LoadedAngularContactBallBearingResults':
        '''LoadedAngularContactBallBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1732.LoadedAngularContactBallBearingResults.TYPE not in self.wrapped.LoadedBearing.__class__.__mro__:
            raise CastException('Failed to cast loaded_bearing to LoadedAngularContactBallBearingResults. Expected: {}.'.format(self.wrapped.LoadedBearing.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LoadedBearing.__class__)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
