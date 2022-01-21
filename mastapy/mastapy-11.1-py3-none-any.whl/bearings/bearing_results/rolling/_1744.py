'''_1744.py

LoadedAxialThrustCylindricalRollerBearingRow
'''


from mastapy.bearings.bearing_results.rolling import _1743, _1746, _1774
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAxialThrustCylindricalRollerBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAxialThrustCylindricalRollerBearingRow',)


class LoadedAxialThrustCylindricalRollerBearingRow(_1774.LoadedNonBarrelRollerBearingRow):
    '''LoadedAxialThrustCylindricalRollerBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAxialThrustCylindricalRollerBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def loaded_bearing(self) -> '_1743.LoadedAxialThrustCylindricalRollerBearingResults':
        '''LoadedAxialThrustCylindricalRollerBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1743.LoadedAxialThrustCylindricalRollerBearingResults.TYPE not in self.wrapped.LoadedBearing.__class__.__mro__:
            raise CastException('Failed to cast loaded_bearing to LoadedAxialThrustCylindricalRollerBearingResults. Expected: {}.'.format(self.wrapped.LoadedBearing.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LoadedBearing.__class__)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
