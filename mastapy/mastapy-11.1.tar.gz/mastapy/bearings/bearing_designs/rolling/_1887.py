'''_1887.py

AxialThrustCylindricalRollerBearing
'''


from mastapy.bearings.bearing_designs.rolling import _1908
from mastapy._internal.python_net import python_net_import

_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'AxialThrustCylindricalRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialThrustCylindricalRollerBearing',)


class AxialThrustCylindricalRollerBearing(_1908.NonBarrelRollerBearing):
    '''AxialThrustCylindricalRollerBearing

    This is a mastapy class.
    '''

    TYPE = _AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AxialThrustCylindricalRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
