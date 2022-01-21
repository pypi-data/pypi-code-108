'''_1787.py

LoadedSphericalRadialRollerBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1788
from mastapy._internal.python_net import python_net_import

_LOADED_SPHERICAL_RADIAL_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedSphericalRadialRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedSphericalRadialRollerBearingElement',)


class LoadedSphericalRadialRollerBearingElement(_1788.LoadedSphericalRollerBearingElement):
    '''LoadedSphericalRadialRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_SPHERICAL_RADIAL_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedSphericalRadialRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
