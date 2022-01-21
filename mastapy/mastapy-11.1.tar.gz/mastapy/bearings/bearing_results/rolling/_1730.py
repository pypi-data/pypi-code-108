'''_1730.py

LoadedAbstractSphericalRollerBearingStripLoadResults
'''


from mastapy.bearings.bearing_results.rolling import _1780
from mastapy._internal.python_net import python_net_import

_LOADED_ABSTRACT_SPHERICAL_ROLLER_BEARING_STRIP_LOAD_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAbstractSphericalRollerBearingStripLoadResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAbstractSphericalRollerBearingStripLoadResults',)


class LoadedAbstractSphericalRollerBearingStripLoadResults(_1780.LoadedRollerStripLoadResults):
    '''LoadedAbstractSphericalRollerBearingStripLoadResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_ABSTRACT_SPHERICAL_ROLLER_BEARING_STRIP_LOAD_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAbstractSphericalRollerBearingStripLoadResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
