'''_659.py

WormGrindingProcessSimulationInput
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _651, _645
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_PROCESS_SIMULATION_INPUT = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingProcessSimulationInput')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingProcessSimulationInput',)


class WormGrindingProcessSimulationInput(_645.ProcessSimulationInput):
    '''WormGrindingProcessSimulationInput

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_PROCESS_SIMULATION_INPUT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingProcessSimulationInput.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def worm_grinder_manufacture_error(self) -> '_651.WormGrinderManufactureError':
        '''WormGrinderManufactureError: 'WormGrinderManufactureError' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_651.WormGrinderManufactureError)(self.wrapped.WormGrinderManufactureError) if self.wrapped.WormGrinderManufactureError is not None else None
