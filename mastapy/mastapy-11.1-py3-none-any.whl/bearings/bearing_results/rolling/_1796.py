'''_1796.py

LoadedTaperRollerBearingDutyCycle
'''


from mastapy.bearings.bearing_results.rolling import _1772
from mastapy._internal.python_net import python_net_import

_LOADED_TAPER_ROLLER_BEARING_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedTaperRollerBearingDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedTaperRollerBearingDutyCycle',)


class LoadedTaperRollerBearingDutyCycle(_1772.LoadedNonBarrelRollerBearingDutyCycle):
    '''LoadedTaperRollerBearingDutyCycle

    This is a mastapy class.
    '''

    TYPE = _LOADED_TAPER_ROLLER_BEARING_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedTaperRollerBearingDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
