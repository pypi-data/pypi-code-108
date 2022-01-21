'''_1888.py

AxialThrustNeedleRollerBearing
'''


from mastapy.bearings.bearing_designs.rolling import _1887
from mastapy._internal.python_net import python_net_import

_AXIAL_THRUST_NEEDLE_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'AxialThrustNeedleRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialThrustNeedleRollerBearing',)


class AxialThrustNeedleRollerBearing(_1887.AxialThrustCylindricalRollerBearing):
    '''AxialThrustNeedleRollerBearing

    This is a mastapy class.
    '''

    TYPE = _AXIAL_THRUST_NEEDLE_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AxialThrustNeedleRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
