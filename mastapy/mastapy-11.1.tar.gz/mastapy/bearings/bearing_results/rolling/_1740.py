'''_1740.py

LoadedAsymmetricSphericalRollerBearingStripLoadResults
'''


from mastapy.bearings.bearing_results.rolling import _1730
from mastapy._internal.python_net import python_net_import

_LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_STRIP_LOAD_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAsymmetricSphericalRollerBearingStripLoadResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAsymmetricSphericalRollerBearingStripLoadResults',)


class LoadedAsymmetricSphericalRollerBearingStripLoadResults(_1730.LoadedAbstractSphericalRollerBearingStripLoadResults):
    '''LoadedAsymmetricSphericalRollerBearingStripLoadResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_STRIP_LOAD_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAsymmetricSphericalRollerBearingStripLoadResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
