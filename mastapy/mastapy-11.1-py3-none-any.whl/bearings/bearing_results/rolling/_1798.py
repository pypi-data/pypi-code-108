'''_1798.py

LoadedTaperRollerBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1773
from mastapy._internal.python_net import python_net_import

_LOADED_TAPER_ROLLER_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedTaperRollerBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedTaperRollerBearingResults',)


class LoadedTaperRollerBearingResults(_1773.LoadedNonBarrelRollerBearingResults):
    '''LoadedTaperRollerBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_TAPER_ROLLER_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedTaperRollerBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
