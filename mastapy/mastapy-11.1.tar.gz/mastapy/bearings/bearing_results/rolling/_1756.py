'''_1756.py

LoadedCylindricalRollerBearingDutyCycle
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1772
from mastapy._internal.python_net import python_net_import

_LOADED_CYLINDRICAL_ROLLER_BEARING_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedCylindricalRollerBearingDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedCylindricalRollerBearingDutyCycle',)


class LoadedCylindricalRollerBearingDutyCycle(_1772.LoadedNonBarrelRollerBearingDutyCycle):
    '''LoadedCylindricalRollerBearingDutyCycle

    This is a mastapy class.
    '''

    TYPE = _LOADED_CYLINDRICAL_ROLLER_BEARING_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedCylindricalRollerBearingDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def permissible_continuous_axial_load_safety_factor(self) -> 'float':
        '''float: 'PermissibleContinuousAxialLoadSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleContinuousAxialLoadSafetyFactor
