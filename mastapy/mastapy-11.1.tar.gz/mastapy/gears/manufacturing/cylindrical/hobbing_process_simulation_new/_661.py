'''_661.py

WormGrindingProcessSimulationViewModel
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _647, _660
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_PROCESS_SIMULATION_VIEW_MODEL = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingProcessSimulationViewModel')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingProcessSimulationViewModel',)


class WormGrindingProcessSimulationViewModel(_647.ProcessSimulationViewModel['_660.WormGrindingProcessSimulationNew']):
    '''WormGrindingProcessSimulationViewModel

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_PROCESS_SIMULATION_VIEW_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingProcessSimulationViewModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
