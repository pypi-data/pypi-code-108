'''_651.py

WormGrinderManufactureError
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _649
from mastapy._internal.python_net import python_net_import

_WORM_GRINDER_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrinderManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrinderManufactureError',)


class WormGrinderManufactureError(_649.RackManufactureError):
    '''WormGrinderManufactureError

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDER_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrinderManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
