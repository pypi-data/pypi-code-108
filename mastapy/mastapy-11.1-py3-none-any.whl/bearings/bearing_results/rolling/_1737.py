'''_1737.py

LoadedAsymmetricSphericalRollerBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1777
from mastapy._internal.python_net import python_net_import

_LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAsymmetricSphericalRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAsymmetricSphericalRollerBearingElement',)


class LoadedAsymmetricSphericalRollerBearingElement(_1777.LoadedRollerBearingElement):
    '''LoadedAsymmetricSphericalRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAsymmetricSphericalRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
