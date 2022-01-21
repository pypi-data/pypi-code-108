'''_625.py

GearMountingError
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _639
from mastapy._internal.python_net import python_net_import

_GEAR_MOUNTING_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'GearMountingError')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMountingError',)


class GearMountingError(_639.MountingError):
    '''GearMountingError

    This is a mastapy class.
    '''

    TYPE = _GEAR_MOUNTING_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMountingError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
