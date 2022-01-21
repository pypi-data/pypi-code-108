'''_1795.py

LoadedSphericalThrustRollerBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1788
from mastapy._internal.python_net import python_net_import

_LOADED_SPHERICAL_THRUST_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSphericalThrustRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSphericalThrustRollerBearingElement',)


class LoadedSphericalThrustRollerBearingElement(_1788.LoadedSphericalRollerBearingElement):
    '''LoadedSphericalThrustRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_SPHERICAL_THRUST_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSphericalThrustRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
