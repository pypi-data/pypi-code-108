'''_634.py

HobbingProcessSimulationViewModel
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _647, _633
from mastapy._internal.python_net import python_net_import

_HOBBING_PROCESS_SIMULATION_VIEW_MODEL = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'HobbingProcessSimulationViewModel')


__docformat__ = 'restructuredtext en'
__all__ = ('HobbingProcessSimulationViewModel',)


class HobbingProcessSimulationViewModel(_647.ProcessSimulationViewModel['_633.HobbingProcessSimulationNew']):
    '''HobbingProcessSimulationViewModel

    This is a mastapy class.
    '''

    TYPE = _HOBBING_PROCESS_SIMULATION_VIEW_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HobbingProcessSimulationViewModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
