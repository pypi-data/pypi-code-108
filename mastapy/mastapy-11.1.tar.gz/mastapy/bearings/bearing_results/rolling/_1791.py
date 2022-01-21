'''_1791.py

LoadedSphericalRollerRadialBearingStripLoadResults
'''


from mastapy.bearings.bearing_results.rolling import _1730
from mastapy._internal.python_net import python_net_import

_LOADED_SPHERICAL_ROLLER_RADIAL_BEARING_STRIP_LOAD_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSphericalRollerRadialBearingStripLoadResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSphericalRollerRadialBearingStripLoadResults',)


class LoadedSphericalRollerRadialBearingStripLoadResults(_1730.LoadedAbstractSphericalRollerBearingStripLoadResults):
    '''LoadedSphericalRollerRadialBearingStripLoadResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_SPHERICAL_ROLLER_RADIAL_BEARING_STRIP_LOAD_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSphericalRollerRadialBearingStripLoadResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
