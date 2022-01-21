'''_676.py

RoughCutterSimulation
'''


from mastapy.gears.manufacturing.cylindrical.cutter_simulation import _671
from mastapy._internal.python_net import python_net_import

_ROUGH_CUTTER_SIMULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'RoughCutterSimulation')


__docformat__ = 'restructuredtext en'
__all__ = ('RoughCutterSimulation',)


class RoughCutterSimulation(_671.GearCutterSimulation):
    '''RoughCutterSimulation

    This is a mastapy class.
    '''

    TYPE = _ROUGH_CUTTER_SIMULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RoughCutterSimulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
