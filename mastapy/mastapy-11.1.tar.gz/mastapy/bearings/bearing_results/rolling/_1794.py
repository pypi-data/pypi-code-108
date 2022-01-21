'''_1794.py

LoadedSphericalRollerThrustBearingStripLoadResults
'''


from mastapy.bearings.bearing_results.rolling import _1780
from mastapy._internal.python_net import python_net_import

_LOADED_SPHERICAL_ROLLER_THRUST_BEARING_STRIP_LOAD_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSphericalRollerThrustBearingStripLoadResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSphericalRollerThrustBearingStripLoadResults',)


class LoadedSphericalRollerThrustBearingStripLoadResults(_1780.LoadedRollerStripLoadResults):
    '''LoadedSphericalRollerThrustBearingStripLoadResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_SPHERICAL_ROLLER_THRUST_BEARING_STRIP_LOAD_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSphericalRollerThrustBearingStripLoadResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
