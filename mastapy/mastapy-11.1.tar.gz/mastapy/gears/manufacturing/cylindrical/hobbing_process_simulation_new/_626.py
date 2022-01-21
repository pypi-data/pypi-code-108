'''_626.py

HobbingProcessCalculation
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _640
from mastapy._internal.python_net import python_net_import

_HOBBING_PROCESS_CALCULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'HobbingProcessCalculation')


__docformat__ = 'restructuredtext en'
__all__ = ('HobbingProcessCalculation',)


class HobbingProcessCalculation(_640.ProcessCalculation):
    '''HobbingProcessCalculation

    This is a mastapy class.
    '''

    TYPE = _HOBBING_PROCESS_CALCULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HobbingProcessCalculation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
