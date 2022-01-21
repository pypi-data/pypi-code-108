'''_1743.py

LoadedAxialThrustCylindricalRollerBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1773
from mastapy._internal.python_net import python_net_import

_LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAxialThrustCylindricalRollerBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAxialThrustCylindricalRollerBearingResults',)


class LoadedAxialThrustCylindricalRollerBearingResults(_1773.LoadedNonBarrelRollerBearingResults):
    '''LoadedAxialThrustCylindricalRollerBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAxialThrustCylindricalRollerBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
