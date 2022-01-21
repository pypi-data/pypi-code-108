'''_1738.py

LoadedAsymmetricSphericalRollerBearingResults
'''


from mastapy.bearings.bearing_results.rolling import _1778
from mastapy._internal.python_net import python_net_import

_LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAsymmetricSphericalRollerBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAsymmetricSphericalRollerBearingResults',)


class LoadedAsymmetricSphericalRollerBearingResults(_1778.LoadedRollerBearingResults):
    '''LoadedAsymmetricSphericalRollerBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAsymmetricSphericalRollerBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
