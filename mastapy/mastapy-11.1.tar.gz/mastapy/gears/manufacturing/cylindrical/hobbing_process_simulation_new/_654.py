'''_654.py

WormGrindingProcessCalculation
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _640
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_PROCESS_CALCULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingProcessCalculation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingProcessCalculation',)


class WormGrindingProcessCalculation(_640.ProcessCalculation):
    '''WormGrindingProcessCalculation

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_PROCESS_CALCULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingProcessCalculation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
