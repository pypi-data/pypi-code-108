'''_668.py

FinishCutterSimulation
'''


from mastapy.gears.manufacturing.cylindrical.cutter_simulation import _671
from mastapy._internal.python_net import python_net_import

_FINISH_CUTTER_SIMULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'FinishCutterSimulation')


__docformat__ = 'restructuredtext en'
__all__ = ('FinishCutterSimulation',)


class FinishCutterSimulation(_671.GearCutterSimulation):
    '''FinishCutterSimulation

    This is a mastapy class.
    '''

    TYPE = _FINISH_CUTTER_SIMULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FinishCutterSimulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
