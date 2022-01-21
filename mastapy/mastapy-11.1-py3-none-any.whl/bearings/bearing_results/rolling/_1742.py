'''_1742.py

LoadedAxialThrustCylindricalRollerBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1776
from mastapy._internal.python_net import python_net_import

_LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAxialThrustCylindricalRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAxialThrustCylindricalRollerBearingElement',)


class LoadedAxialThrustCylindricalRollerBearingElement(_1776.LoadedNonBarrelRollerElement):
    '''LoadedAxialThrustCylindricalRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAxialThrustCylindricalRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
