'''_1807.py

LoadedToroidalRollerBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1778
from mastapy._internal.python_net import python_net_import

_LOADED_TOROIDAL_ROLLER_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedToroidalRollerBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedToroidalRollerBearingResults',)


class LoadedToroidalRollerBearingResults(_1778.LoadedRollerBearingResults):
    '''LoadedToroidalRollerBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_TOROIDAL_ROLLER_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedToroidalRollerBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
