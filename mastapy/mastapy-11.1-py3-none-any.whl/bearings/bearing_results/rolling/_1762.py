'''_1762.py

LoadedDeepGrooveBallBearingRow
'''


from mastapy.bearings.bearing_results.rolling import _1761, _1752
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_LOADED_DEEP_GROOVE_BALL_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedDeepGrooveBallBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedDeepGrooveBallBearingRow',)


class LoadedDeepGrooveBallBearingRow(_1752.LoadedBallBearingRow):
    '''LoadedDeepGrooveBallBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_DEEP_GROOVE_BALL_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedDeepGrooveBallBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def loaded_bearing(self) -> '_1761.LoadedDeepGrooveBallBearingResults':
        '''LoadedDeepGrooveBallBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1761.LoadedDeepGrooveBallBearingResults)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
