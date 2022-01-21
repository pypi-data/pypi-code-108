'''_1770.py

LoadedNeedleRollerBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1758
from mastapy._internal.python_net import python_net_import

_LOADED_NEEDLE_ROLLER_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedNeedleRollerBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedNeedleRollerBearingResults',)


class LoadedNeedleRollerBearingResults(_1758.LoadedCylindricalRollerBearingResults):
    '''LoadedNeedleRollerBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_NEEDLE_ROLLER_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedNeedleRollerBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
