'''_1746.py

LoadedAxialThrustNeedleRollerBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1743
from mastapy._internal.python_net import python_net_import

_LOADED_AXIAL_THRUST_NEEDLE_ROLLER_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAxialThrustNeedleRollerBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAxialThrustNeedleRollerBearingResults',)


class LoadedAxialThrustNeedleRollerBearingResults(_1743.LoadedAxialThrustCylindricalRollerBearingResults):
    '''LoadedAxialThrustNeedleRollerBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_AXIAL_THRUST_NEEDLE_ROLLER_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAxialThrustNeedleRollerBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
