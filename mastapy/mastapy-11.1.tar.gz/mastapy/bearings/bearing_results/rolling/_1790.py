'''_1790.py

LoadedSphericalRollerRadialBearingRow
'''


from mastapy.bearings.bearing_results.rolling import _1789, _1779
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_LOADED_SPHERICAL_ROLLER_RADIAL_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSphericalRollerRadialBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSphericalRollerRadialBearingRow',)


class LoadedSphericalRollerRadialBearingRow(_1779.LoadedRollerBearingRow):
    '''LoadedSphericalRollerRadialBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_SPHERICAL_ROLLER_RADIAL_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSphericalRollerRadialBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def loaded_bearing(self) -> '_1789.LoadedSphericalRollerRadialBearingResults':
        '''LoadedSphericalRollerRadialBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1789.LoadedSphericalRollerRadialBearingResults)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
