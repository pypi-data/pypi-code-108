'''_1741.py

LoadedAxialThrustCylindricalRollerBearingDutyCycle
'''


from mastapy.bearings.bearing_results.rolling import _1772
from mastapy._internal.python_net import python_net_import

_LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedAxialThrustCylindricalRollerBearingDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedAxialThrustCylindricalRollerBearingDutyCycle',)


class LoadedAxialThrustCylindricalRollerBearingDutyCycle(_1772.LoadedNonBarrelRollerBearingDutyCycle):
    '''LoadedAxialThrustCylindricalRollerBearingDutyCycle

    This is a mastapy class.
    '''

    TYPE = _LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedAxialThrustCylindricalRollerBearingDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
